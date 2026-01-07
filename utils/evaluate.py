import re
from fractions import Fraction
from typing import Optional, Dict, Any

prompt_template = """[GOAL]
Given a **Question**, **Response**, and a natural-language **Checklist**, decide for each checklist item whether the Response **explicitly** satisfies it: **met = 1**, **not met = 0**. Final score = **(# met) / (total checklist items)**.

[INPUT]
[Question]
{{QUESTION}}

[Response]
{{RESPONSE}}

[Checklist]
{{CHECKLIST}}  ← JSON array or a plain list string. Treat each string as one criterion. Strip any leading numbering like “1.” or “2)”.

[DECISION RULES]
1. **Use only the Response text.** No outside knowledge/assumptions. If uncertain → 0.
2. **Explicitness (mentions/explains/indicates).**
   * 1: Clear, direct statement that fulfills the criterion.
   * 0.5: Indirect/implicit mention that likely implies fulfillment, but not explicit.
   * 0: Not mentioned or contradicted.
   
3. **“All / every / complete” requirements.**
   * 1: Explicitly states completeness (e.g., “all”, “every”, or equivalent).
   * 0.5: Strongly suggests near-completeness (“fill the nests” without “all”, “almost all”).
   * 0: No completeness requirement or states partial suffices.
   
4. **Method / Procedure (“explains how / method”).**
   * 1: Concrete, actionable steps or clear guidance.
   * 0.5: Vague or partial steps (general approach without specifics).
   * 0: No method/procedure provided.
   
5. **“Various / multiple types.”**
   * 1: Names **≥2 distinct, specific types**.
   * 0.5: Mentions variety without naming types, or names only **1** type.
   * 0: No indication of multiple types.
   
6. **Synonyms.** Accept unambiguous equivalents (e.g., “baby dragon” = “hatchling”).
   * 1: Unambiguous equivalence.
   * 0.5: Likely equivalent but slightly ambiguous.
   * 0: Ambiguous or different meaning.

[Evidence policy]
* For **met = 1 or 0.5**, include a **10–60 character direct quote** from the Response supporting the decision.
* For **met = 0 ** include a brief explanation why the response fails the given criteria.
* In the evidence block, list **evidence first**, then the explanation, then the met value.

[OUTPUT FORMAT — STRICT. NO PROSE OUTSIDE TAGS.] <evidence>
Item 1:
evidence: "…direct quote from Response…"
explanation: Briefly justify why criterion 1 earned 1/0.5/0 (reference rule numbers if helpful).
met: 0 | 0.5 | 1

Item 2:
evidence: "…"
explanation: …
met: 0 | 0.5 | 1

… (repeat for all checklist items, in order) </evidence>
<score>
K/N 
</score>

[NOTES]
* Output **only** the two tags above; no code fences, no extra text."""

# Matches either a fraction (e.g., 0.5/5) or a single number (e.g., 0.25) inside <score> tags.
SCORE_RE = re.compile(
    r"""<score>\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*(?:/\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*)?</score>""",
    re.IGNORECASE | re.DOTALL,
)

def parse_single_score(text: str, *, max_denominator: int = 100000) -> Optional[Dict[str, Any]]:
    """
    Parse exactly one <score>...</score> block from text.

    - Accepts either 'num/den' or a standalone number inside the tag.
    - On 0 tags: print the full text for debugging and return None.
    - On >1 tags: raises ValueError.

    Returns a dict with:
      {
        "value": float,                 # decimal value
        "value_frac": "p/q",            # reduced fraction as string
        "numerator_raw": float|None,    # as written (if 'num/den' was used)
        "denominator_raw": float|None,  # as written (if 'num/den' was used)
        "numerator": int,               # reduced numerator of the value
        "denominator": int              # reduced denominator of the value
      }
    """
    matches = SCORE_RE.findall(text)

    if not matches:
        print("DEBUG: no <score> tag found. Full response below:\n" + text)
        return None

    if len(matches) > 1:
        raise ValueError(f"Expected 1 <score> tag, found {len(matches)}")

    num_s, den_s = matches[0]

    if den_s:  # fraction form like "0.5/5"
        num_raw = float(num_s)
        den_raw = float(den_s)
        if den_raw == 0:
            raise ZeroDivisionError("Denominator is 0 in <score>")

        # Exact rational value (reduced)
        val_frac = (Fraction(num_s).limit_denominator(max_denominator)
                    / Fraction(den_s).limit_denominator(max_denominator))
    else:      # single number form like "0.25"
        num_raw = None
        den_raw = None
        # Convert decimal to reduced rational (e.g., 0.25 -> 1/4)
        val_frac = Fraction(num_s).limit_denominator(max_denominator)

    value = float(val_frac)
    return {
        "value": value,
        "value_frac": f"{val_frac.numerator}/{val_frac.denominator}",
        "numerator_raw": num_raw,
        "denominator_raw": den_raw,
        "numerator": val_frac.numerator,
        "denominator": val_frac.denominator,
    }