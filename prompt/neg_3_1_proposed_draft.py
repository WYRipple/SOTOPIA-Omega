neg_3_1_proposed_draft = """
{head_prompt}

{background_prompt}

{history_turn}

The last two Turns are your conflict and status analysis with the other party, based on and in the following order of thought:
step1. Elaborate on what your conflicts are (e.g., money, concept, values) and emphasize that the subsequent strategy cannot be designed based on the conflicting items.
step2. Elaborate on which additional matters could effectively supplement the other party's slightly compromised conflicting interests.
step3. Analyze these additional matters to determine whether they will avoid causing harm to your own interests.
step4. Based on matters the other party values without harming your interests, draft a proposal offering **tangible benefits** beyond the conflict to compensate for their core conflicting interests.
step5. Further explain these **tangible benefits** and clarify why they can **serve as a practical complement** to the goals the other party cannot achieve.

Please only generate a JSON string. The JSON string response should follow the given format:
{{"thought":{{"step1":"","step2":"","step3":"","step4":"","step5":""}}}}
"""