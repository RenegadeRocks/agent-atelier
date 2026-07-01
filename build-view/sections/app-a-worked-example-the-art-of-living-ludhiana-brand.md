<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §app-a (source lines 2648–2738). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## Appendix A — Worked example: the Art of Living Ludhiana Brand Kit (filled)

What the *current* AOL system looks like expressed as one Brand Kit (proof the generalization is faithful):

```yaml
brand_kit_version: 2
brand_name: "Art of Living Ludhiana"
brand_short_name: "Art of Living · Ludhiana"
tagline: "Wellness, breath, and meditation for the householder"
locale: "Ludhiana, Punjab, India"
languages: ["Hindi", "Punjabi", "English"]
timezone: "Asia/Kolkata"
mission: "Ready-to-publish, research-grounded wellness & meditation content that is never wrong, never repetitive, never drab."
brand_type: "educational"

audience_persona: "a 32-year-old shop owner on Ferozepur Road; the auntie running a household; the uncle balancing shop and family"
audience_pains: ["stress", "poor sleep", "overwhelm", "no time to practice"]
scroll_test_persona: "the 32-year-old shop owner scrolling at the shutter at 6:40pm"

voice_descriptors: ["warm", "practical", "never preachy", "invitational"]
voice_do: ["lead with value", "name the Ludhiana day specifically", "one small thing to try today"]
voice_dont: ["fear hooks", "listicle slop", "fake urgency", "medical claims", "politics", "paraphrasing Sri Sri without citation"]

logo_asset: "assets/aol_logo.png"
wordmark_text: "Ludhiana"
palette_hex: ["#F07020", "#F09020", "#F0B020", "#F0D020"]
accent_dark_bg: "#F2C12E"
accent_light_bg: "#B8800E"
headline_font: "Georgia Bold"
label_font: "Futura (small caps)"
visual_register: "premium, warm, real Indian/Punjab life; NOT spa/stock-wellness/brochure; variety by message"
visual_variety: "balanced"
visual_strategy: "concept_led"
people_pool: "assets/people/"
product_pool: "assets/products/"
image_provider: "replicate_gpt_image"   # AOL's current choice; recommended Google-native swap: gemini_image_pro / Nano Banana Pro (confirm exact IDs at build time)
image_quality_tier: "medium"

cta_style: "soft"
contact_whatsapp: ["+91 82839 36382", "+91 82839 00163"]
contact_instagram: "@artofliving_ldhtok"
cta_forbidden_phrases: ["register now", "book now", "sign up", "only X spots left"]

channels: ["instagram", "facebook"]
posts_per_week_target: 5
standing_week:
  mon: { track: "evergreen" }
  tue: { track: "offering:sahaj_samadhi" }
  wed: { track: "evergreen", flag: "research_grounded" }
  thu: { track: "offering:happiness_program" }
  fri: { track: "evergreen" }
  weekend: { track: "optional" }
research_post_min_per_week: 1
max_posts_per_week: 6

claims_allowed: ["'reduces stress' with citation", "population-level study figures with hedge + named source"]
claims_forbidden: ["'cures depression'", "'replaces therapy/medication'", "100% outcome claims", "invented citations"]
comparative_claims_allowed: false
political_content_allowed: false
non_disclosure_rules:
  - "Sahaj Samadhi mantra and how it is received/repeated — never in words or image"
  - "Sudarshan Kriya exact rhythm/mechanism — ceiling is 'a cyclical breathing rhythm'"
required_framing:
  - { topic: "clinical-population research (PTSD, depression)", framing: "'in clinical studies' + never implying treatment replacement" }
source_allowlist: ["peer-reviewed journals", "PubMed", "publisher pages", "Patanjali Yoga Sutras", "Sri Sri published works", "AOL canon"]
source_denylist: ["blogs", "forums", "reddit", "secondary wellness sites"]
citation_required_for_claims: true
require_second_source_for_quantitative: true   # clinical outcome stats are high-stakes
claim_reverify_months: 6

offerings:
  - { id: "happiness_program", name: "The Happiness Program", is_flagship: true,
      one_liner: "A multi-session course whose heart is Sudarshan Kriya — rhythmic breathing + practical tools for mind and emotions; experiential, never 'just journaling'." }
  - { id: "sahaj_samadhi", name: "Sahaj Samadhi Dhyaan Yoga", funnels_from: "happiness_program",
      one_liner: "An effortless mantra-based meditation, ~20 minutes, deeply restful; the mind settles without effort. (Mechanics never revealed.)" }
  # Sahaj Offering Brief tone notes: "the brand voice at half the volume — quieter, more interior;
  # audience is mostly Happiness Program graduates; introduce only once matured; never aggressive."

evergreen_pillars: ["stress & modern life", "sleep & rhythms", "breath as daily practice", "mind & emotion", "householder spirituality", "sattvic food", "seva"]
local_detail_bank: ["morning chai", "Ferozepur Road scooter traffic", "shop shutters at 6:40", "school run", "power cuts", "wedding season", "kanak harvest", "langar seva", "the 4:50am train horn", "rooftop charpais in June"]

approval_mode: "human"
auto_publish_enabled: false
system_of_record: "google_sheets"
trust_threshold: { window_pieces: 20, min_approval_rate: 0.95, max_avg_human_edits: 0, zero_policy_violations: true }
```

The AOL Offering Briefs (Happiness Program, Sahaj Samadhi) and the evergreen territory map onto `offerings[]` Offering Briefs + `evergreen_pillars` — the same content the AOL agents load today, now as Brand-Kit-attached dynamic context selected per task.

---

