# Session 03 — Pydantic: validation and schemas

**FastAPI course · 3 hours**

## Goal
Stop trusting the client. Describe every piece of data that enters or leaves
the API with a Pydantic model: which fields exist, which are required, what
values are allowed, and what the client is allowed to *see*. Understand the
difference between the data we **store**, the data we **accept** and the data
we **return** — the Create / Update / Read pattern that the rest of the course
builds on.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 45 | lax conversion vs errors, `Field`, validators, why three schemas |
| Practice | 110 | examples 01–09, "predict the result" (07), then `10_project` |
| Review | 25 | break every rule from Bruno, read the 422s, homework |

**Practical share: about 75%.**

## Python you already know, used again
Classes and inheritance (`CourseBase` → `CourseCreate`) · dataclasses (Pydantic
feels the same) · type hints, `Literal`, `X | None` · `Annotated` · decorators
(`@field_validator`) · class methods · exceptions (`ValidationError`,
`ValueError`) · properties (`@computed_field`).

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* `BaseModel`, lax conversion (`"42"` → `42`), `ValidationError` and its `errors()`
* `model_validate()` (from a dict) and `model_validate_json()` (from text)
* `Field(...)`: `min_length`, `max_length`, `ge`, `gt`, `le`, `pattern`, `description`
* Reusable constrained types with `Annotated`
* Required vs default vs optional, and the `str | None` without default trap
* `model_fields_set` and `model_dump(exclude_unset=True)` for PATCH
* Nested models and lists of models; error locations like `('sessions', 1, 'number')`
* `@field_validator`, `@model_validator(mode='after')`, `EmailStr`
* `model_dump`, `model_dump_json`, `include` / `exclude`, `@computed_field`
* `from_attributes=True` — reading objects, not only dicts (session 5 needs it)
* Response models: the return type filters what leaves the API
* Create / Update / Read schemas, and why the database model is a fourth class

## Examples
| Folder | Topic |
|--------|-------|
| `01_basemodel` | Conversion, errors, `model_validate` |
| `02_field_constraints` | `Field` rules and reusable `Annotated` types |
| `03_optional_and_defaults` | Required / default / optional, `model_fields_set` |
| `04_nested_models` | Models inside models, error paths |
| `05_custom_validators` | `field_validator`, `model_validator`, `EmailStr` |
| `06_serialization` | `model_dump`, `computed_field`, `from_attributes` |
| `07_diagnose_validation` | **Predict** pass or fail for 12 payloads, then run |
| `08_response_model` | Hiding the password hash with a response model |
| `09_create_update_read` | Three schemas for one resource |
| `10_project` | **Project:** Training Center API v2 with `schemas.py` + Bruno |

## How to run
Examples 01–07 are plain scripts:
```bash
cd 01_basemodel
python app.py
```
Examples 08–09 are servers (`python app.py`, then `/docs`). The project:
```bash
cd 10_project
python main.py
```
Open `10_project/bruno` in Bruno and run the whole collection with the Runner.

## Exercises
See `exercises.md`.
