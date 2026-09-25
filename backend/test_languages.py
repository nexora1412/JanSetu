"""
JanSetu — language detection test  (run this, it takes 2 seconds)
=================================================================
Proves the Marathi/Hindi split works. Devanagari is ONE script shared by TWO
languages, so "is this Devanagari?" is not enough — you must also decide
Marathi vs Hindi. That was the bug; this is the proof it is fixed.

HOW TO RUN
----------
    cd backend
    python test_languages.py

WHAT GOOD LOOKS LIKE
--------------------
    10/10 passed

WHY IT MATTERS FOR THE DEMO
---------------------------
If a Marathi complaint is labelled Hindi, the citizen gets an SMS reply in the
wrong language. Judges notice that instantly. This test is the guard.
"""
from __future__ import annotations

from services.telephony.base import TelephonyProvider

# (text, expected language code)
CASES: list[tuple[str, str]] = [
    ("धुळे तालुक्यात रस्ता खराब आहे", "mr"),
    ("पाण्याची समस्या आहे खूप", "mr"),
    ("मला पाणी पाहिजे", "mr"),
    ("आम्ही पाण्यासाठी त्रस्त आहोत", "mr"),
    ("गावात रस्ते खराब झाले आहेत", "mr"),
    ("सड़क खराब है", "hi"),
    ("मेरा नाम राम है", "hi"),
    ("पानी नहीं आ रहा है", "hi"),
    ("बिजली नहीं है गांव में", "hi"),
    ("road is broken near the school", "en"),
]


def main() -> None:
    print("=" * 62)
    print("LANGUAGE DETECTION")
    print("=" * 62)

    passed = 0
    for text, expected in CASES:
        got = TelephonyProvider.detect_language(text)
        ok = got == expected
        passed += ok
        flag = "OK  " if ok else "FAIL"
        print(f"  {flag}  expected={expected:3}  got={got:3}   {text}")

    print()
    print(f"  {passed}/{len(CASES)} passed")

    if passed == len(CASES):
        print("  >>> PASS — Marathi and Hindi are being told apart.")
    else:
        print("  >>> FAILURES PRESENT. Do not change code.")
        print("  >>> Copy this whole output into the group chat.")


if __name__ == "__main__":
    main()
