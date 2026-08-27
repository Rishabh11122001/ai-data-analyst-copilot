import os
import time
from pathlib import Path

from dotenv import load_dotenv

from google import genai
from google.genai import errors as gemini_errors

import groq
from groq import Groq


# =========================================================
# ENVIRONMENT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# =========================================================
# GEMINI CONFIG
# =========================================================

GEMINI_KEYS = [
    os.getenv(f"GEMINI_API_KEY_{i}")
    for i in range(1, 8)
]

GEMINI_KEYS = [
    key for key in GEMINI_KEYS
    if key
]

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.7-flash"
)

GEMINI_FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# GROQ CONFIG
# =========================================================

GROQ_KEYS = [
    os.getenv(f"GROQ_API_KEY_{i}")
    for i in range(1, 5)
]

GROQ_KEYS = [
    key for key in GROQ_KEYS
    if key
]

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# =========================================================
# CONFIG VALIDATION
# =========================================================

if not GEMINI_KEYS and not GROQ_KEYS:
    raise ValueError(
        "No Gemini or Groq API keys were found in .env."
    )


# =========================================================
# HELPER
# =========================================================

def get_status_code(error):

    return (
        getattr(error, "code", None)
        or getattr(error, "status_code", None)
    )


# =========================================================
# GEMINI PROVIDER
# =========================================================

def generate_with_gemini(
    prompt: str,
    max_retries: int = 2
):

    if not GEMINI_KEYS:
        raise RuntimeError(
            "No Gemini API keys configured."
        )

    models = [
        GEMINI_MODEL,
        GEMINI_FALLBACK_MODEL
    ]

    last_error = None


    # -----------------------------------------------------
    # Multiple keys are used for credential redundancy.
    #
    # We do NOT cycle accounts simply to bypass
    # rate-limit/quota restrictions.
    # -----------------------------------------------------

    for key_number, api_key in enumerate(
        GEMINI_KEYS,
        start=1
    ):

        client = genai.Client(
            api_key=api_key
        )

        authentication_failed = False


        for model in models:

            for attempt in range(max_retries):

                try:

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    if not response.text:

                        raise RuntimeError(
                            "Gemini returned an empty response."
                        )


                    print(
                        f"LLM Provider: Gemini | "
                        f"Model: {model}"
                    )

                    return response.text


                # -----------------------------------------
                # Gemini client errors
                # -----------------------------------------

                except gemini_errors.ClientError as e:

                    last_error = e

                    status = get_status_code(e)


                    # Invalid / unauthorized credential
                    if status in (401, 403):

                        print(
                            f"Gemini key {key_number} "
                            f"is invalid or unauthorized."
                        )

                        authentication_failed = True

                        break


                    # Quota / rate limit
                    if status == 429:

                        print(
                            f"Gemini model {model} "
                            f"quota/rate limit reached."
                        )

                        # Try Gemini fallback model,
                        # then move to Groq.
                        break


                    raise


                # -----------------------------------------
                # Gemini server errors
                # -----------------------------------------

                except gemini_errors.ServerError as e:

                    last_error = e

                    if attempt < max_retries - 1:

                        wait_time = 2 ** attempt

                        print(
                            f"Gemini {model} temporarily "
                            f"unavailable. Retrying in "
                            f"{wait_time}s..."
                        )

                        time.sleep(wait_time)

                    else:

                        print(
                            f"Gemini {model} unavailable."
                        )


                except Exception as e:

                    last_error = e
                    raise


            if authentication_failed:
                break


        # Only try another key when the current
        # credential itself is invalid/unusable.
        if not authentication_failed:
            break


    raise RuntimeError(
        "Gemini is currently unavailable."
    ) from last_error


# =========================================================
# GROQ PROVIDER
# =========================================================

def generate_with_groq(prompt: str):

    if not GROQ_KEYS:

        raise RuntimeError(
            "No Groq API keys configured."
        )


    last_error = None


    for key_number, api_key in enumerate(
        GROQ_KEYS,
        start=1
    ):

        try:

            client = Groq(
                api_key=api_key,
                max_retries=0,
                timeout=30.0
            )


            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )


            text = completion.choices[0].message.content


            if not text:

                raise RuntimeError(
                    "Groq returned an empty response."
                )


            print(
                f"LLM Provider: Groq | "
                f"Model: {GROQ_MODEL}"
            )


            return text


        # ---------------------------------------------
        # Invalid key
        # ---------------------------------------------

        except (
            groq.AuthenticationError,
            groq.PermissionDeniedError
        ) as e:

            last_error = e

            print(
                f"Groq key {key_number} "
                f"is invalid or unauthorized."
            )

            # Credential redundancy:
            # try next configured key
            continue


        # ---------------------------------------------
        # Rate limit
        # ---------------------------------------------

        except groq.RateLimitError as e:

            last_error = e

            print(
                "Groq rate limit reached."
            )

            break


        # ---------------------------------------------
        # Server / network failure
        # ---------------------------------------------

        except (
            groq.InternalServerError,
            groq.APIConnectionError,
            groq.APITimeoutError
        ) as e:

            last_error = e

            print(
                "Groq temporarily unavailable."
            )

            break


        except Exception as e:

            last_error = e

            raise


    raise RuntimeError(
        "Groq is currently unavailable."
    ) from last_error


# =========================================================
# MAIN LLM ROUTER
# =========================================================

def generate_text(prompt: str) -> str:

    gemini_error = None
    groq_error = None


    # -----------------------------------------------------
    # Provider 1: Gemini
    # -----------------------------------------------------

    try:

        return generate_with_gemini(
            prompt
        )

    except Exception as e:

        gemini_error = e

        print(
            "Gemini unavailable. "
            "Switching to Groq..."
        )


    # -----------------------------------------------------
    # Provider 2: Groq
    # -----------------------------------------------------

    try:

        return generate_with_groq(
            prompt
        )

    except Exception as e:

        groq_error = e


    # -----------------------------------------------------
    # Complete provider failure
    # -----------------------------------------------------

    raise RuntimeError(
        "All configured LLM providers are currently "
        "unavailable."
    ) from (
        groq_error or gemini_error
    )


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    test_prompt = """
You are an AI data analyst.

Reply with exactly one short sentence confirming
that you are ready to analyze PostgreSQL business data.
"""

    try:

        response = generate_text(
            test_prompt
        )

        print("\nLLM Response:")
        print(response)

    except Exception as e:

        print("\nLLM test failed:")
        print(e)