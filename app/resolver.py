import re
import os
import pathlib

class Err:
    def __init__(self, code, context):
        self.code = code
        self.context = context
    def __str__(self):
        return f"{self.code}: {self.context}"
    def __repr__(self):
        return self.__str__()
    def __eq__(self, other):
        return type(self) == type(other) and self.code == other.code and self.context == other.context

class ResolveBlocked(Exception):
    def __init__(self, errors):
        self.errors = errors
    def __str__(self):
        return f"Resolution blocked: {self.errors}"

MODEL = "MODEL"
AUTH = "AUTH"

class ResolveScope:
    def __init__(self, target: str, binding: dict = None):
        self.target = target
        self.binding = binding or {}
        self.auth_secrets = {}

    def auth_bind(self, token, value):
        self.auth_secrets[token] = value

class Spec:
    def __init__(self, field, req, serialization, target, default=None, env_key=None, condition=None, allow_literal_brackets=False):
        self.field = field
        self.req = req
        self.serialization = serialization
        self.target = target
        self.default = default
        self.env_key = env_key
        self.condition = condition
        self.allow_literal_brackets = allow_literal_brackets

    def required_in(self, brand_kit):
        if "required" in self.req.lower():
            return True
        if "cond" in self.req.lower():
            if self.condition:
                return self.condition(brand_kit)
            return True
        return False

REGISTRY = {}
def _load_registry():
    md_path = pathlib.Path(__file__).parent.parent / 'specs' / 'resolver.md'
    if not md_path.exists():
        return
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('| `[[') and ']]` |' in line:
            # use ' | ' to avoid breaking on \|
            parts = [p.strip() for p in line.split(' | ')]
            if len(parts) >= 5:
                # Due to first '|', parts[0] is empty, parts[1] is token, parts[2] is field...
                # Actually, let's just strip the leading and trailing '|'
                line = line.strip('|')
                parts = [p.strip() for p in line.split(' | ')]
                if len(parts) >= 5:
                    token = parts[0].replace('`', '').replace('[', '').replace(']', '').strip()
                    field = parts[1].replace('`', '').strip()
                    req = parts[2].strip()
                    serialization = parts[3].replace('`', '').replace('\\|', '|').strip()
                    target_str = parts[4].strip()
                target_enum = AUTH if 'auth' in target_str.lower() and 'model' not in target_str.lower() else MODEL
                
                # Handling defaults and conditions
                default = None
                condition = None
                if token == "READING_LEVEL": default = "plain, conversational"
                elif token == "SOURCE_DENYLIST": default = ["blogs", "forums", "reddit", "unverified social"]
                elif token == "CLAIM_REVERIFY_MONTHS": default = 6
                elif token == "REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE": default = False
                elif token == "RESEARCH_POST_MIN_PER_WEEK": default = 1
                elif token == "CTA_FORBIDDEN_PHRASES": default = ["register now", "book now", "sign up", "limited spots"]
                elif token == "VISUAL_VARIETY": default = "balanced"
                elif token == "VISUAL_STRATEGY": default = "concept_led"
                elif token == "IMAGE_PROVIDER": default = "gemini_image_pro"
                elif token == "IMAGE_QUALITY_TIER": default = "medium"
                elif token == "TRUST_THRESHOLD":
                    condition = lambda bk: bk.get("approval_mode") == "auto_after_trust"
                elif token == "PRODUCT_POOL":
                    condition = lambda bk: bk.get("visual_strategy") == "product_led"
                
                REGISTRY[token] = Spec(field=field, req=req, serialization=serialization, target=target_enum, default=default, condition=condition)

    # Add metasyntactic tokens that appear literally in agent prompts
    REGISTRY["VARIABLE"] = Spec(field="", req="optional", serialization="scalar", target=MODEL, default="[[VARIABLE]]", allow_literal_brackets=True)
    REGISTRY["TOKEN"] = Spec(field="", req="optional", serialization="scalar", target=MODEL, default="[[TOKEN]]", allow_literal_brackets=True)
    REGISTRY["BRAND_TYPE"] = Spec(field="brand_type", req="optional", serialization="scalar", target=MODEL)
    REGISTRY["OFFERING_ID"] = Spec(field="", req="optional", serialization="scalar", target=MODEL, default="")

_load_registry()

PLACEHOLDER = r"\[\[([A-Z0-9_:]+)\]\]"

def _is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False

def _lookup(brand_kit, field_path, binding):
    if not field_path:
        return None
    if field_path.startswith('offerings[].'):
        subfield = field_path.split('.')[1]
        return binding.get(f'OFFERING_{subfield.upper()}')
    
    parts = field_path.split('.')
    curr = brand_kit
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr

def _serialize(value, kind, directive):
    form = directive or kind.split('\\|')[0].split('|')[0]
    if form == "scalar":
        return str(value).strip()
    elif form == "bool":
        return "true" if value else "false"
    elif form == "int":
        return str(int(value))
    elif form == "hex":
        return str(value).upper()
    elif form == "path":
        return str(value)
    elif form == "comma":
        if isinstance(value, list):
            return ", ".join(map(str, value))
        return str(value)
    elif form == "bullet":
        if isinstance(value, list):
            return "\n".join(f"- {x}" for x in value)
        return f"- {value}"
    elif form == "object:framing-list":
        if isinstance(value, list):
            return "\n".join(f"- topic: {e.get('topic')} — framing: {e.get('framing')}" for e in value)
        return ""
    elif form == "object:week-map":
        if isinstance(value, dict):
            lines = []
            for day, slots in value.items():
                kv = ", ".join(f"{k}={v}" for k,v in slots.items())
                lines.append(f"- {day}: {kv}")
            return "\n".join(lines)
        return ""
    elif form == "object:trust-block":
        if isinstance(value, dict):
            return "\n".join(f"- {k}={v}" for k, v in value.items())
        return ""
    elif form == "object:offering-list":
        if isinstance(value, list):
            return "\n".join(f"- {o.get('name')} — {o.get('one_liner')}" for o in value)
        return ""
    else:
        return str(value)

class SecretsVault:
    def __init__(self, secrets):
        self.secrets = secrets
    def has(self, ref):
        return ref in self.secrets
    def fetch(self, ref):
        return self.secrets[ref]

def resolve(template, brand_kit, env, vault, scope):
    errors = []
    out = []
    cursor = 0

    for match in re.finditer(PLACEHOLDER, template):
        out.append(template[cursor:match.start()])
        cursor = match.end()
        token = match.group(1)
        
        directive = None
        lookahead = template[cursor:cursor+20]
        dir_match = re.search(r'^\s*<!--(bullet|comma)-->', lookahead)
        if dir_match:
            directive = dir_match.group(1)

        if token.startswith("SECRET:"):
            if scope.target != AUTH:
                errors.append(Err("ERR_SECRET_IN_MODEL_CONTEXT", token))
                continue
            
            if token == "SECRET:IMAGE_PROVIDER_KEY":
                provider = brand_kit.get('image_provider', 'gemini_image_pro')
                ref = f"{provider}_api_key"
            elif token == "SECRET:GOOGLE_TOKEN":
                ref = "google_oauth_token"
            elif token == "SECRET:INSTAGRAM_TOKEN":
                ref = "instagram_graph_token"
            else:
                ref = token.replace("SECRET:", "").lower()
                
            if not vault.has(ref):
                errors.append(Err("ERR_SECRET_MISSING", token))
                continue
            scope.auth_bind(token, vault.fetch(ref))
            continue

        spec = REGISTRY.get(token)
        if spec is None:
            # Special case for offerings in the template loop
            if token in ["OFFERING_ID", "OFFERING_NAME", "OFFERING_BRIEF"]:
                value = scope.binding.get(token)
                if _is_empty(value):
                    errors.append(Err("ERR_REQUIRED_UNRESOLVED", token))
                    continue
                out.append(str(value))
                continue
            errors.append(Err("ERR_UNKNOWN_TOKEN", token))
            continue
            
        if spec.target == AUTH:
            errors.append(Err("ERR_BRAND_TOKEN_NOT_FOR_AUTH", token))
            continue

        value = _lookup(brand_kit, spec.field, scope.binding)
        if _is_empty(value):
            if env is not None and spec.env_key is not None and spec.env_key in env:
                value = env.get(spec.env_key)
        if _is_empty(value):
            value = spec.default
            
        if _is_empty(value):
            if spec.required_in(brand_kit):
                errors.append(Err("ERR_REQUIRED_UNRESOLVED", token))
                continue
            value = ""

        literal = _serialize(value, spec.serialization, directive)
        if "[[" in literal and not spec.allow_literal_brackets:
            errors.append(Err("ERR_RECURSION_DETECTED", token))
            
        out.append(literal)

    out.append(template[cursor:])

    if errors:
        raise ResolveBlocked(errors)

    return "".join(out)
