neg_0_change_style = """
Turn the given conversation into a more conversational tone, making it sound like a real dialogue, without changing any core meaning.

Provide some personality and background information (the information about both parties involved in the conversation.):
{profile}

What the other person said in the previous round:
{last_speak}

**The speak that requires style modification:**
{speak}

Style change metric:
1. Only output the content, **without quotation marks and line breaks**. 
2. Do not change the original content and logic of the statement; only polish for contextual coherence and style.
3. Avoid using expressions like "1. 2. 3." and opt for a more natural style instead.
4. Be consistent with the previous round.
5. For specific words ("benefits", "matters", "goals", "conflict"), appropriately adjust the expression to better match the personality and background of the character profile."
6. New style is like having a real conversation as a person.
7. Slightly streamline the conversation, but do not reduce the points and ideas.
Style change begin:
"""