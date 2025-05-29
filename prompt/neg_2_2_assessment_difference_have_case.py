neg_2_2_assessment_difference_have_case = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

In your previous thoughts, you obtained your utility list and also inferred the other party's utility list.

**What is the utility list?**
A utility list is a structured representation of all relevant matters in a negotiation, each characterized by its introduction, explanation, and associated values. This list helps quantify the subjective importance of different factors and their contribution to achieving personal goals in a negotiation.
Each entry in the utility list consists of the following components:
Matter Introduction and Explanation:
- This is a clear description of the matter, outlining its specific nature and why it is important to the individual. The explanation includes the matter's connection to personal goals, emotional benefits, or broader strategic considerations.
Matter Value:
- Value: Represents the target or maximum value the individual would ideally achieve for this matter in a perfect scenario.
- Weight Factor: Indicates the relative importance of this matter compared to others in the list. The weight factor ensures that the overall utility score remains balanced and reflects the negotiator's preferences.

**Your utility list**
{my_utility}

**Guess other part utility list**
{other_utility}

Based on your and the other party's utility lists, think in the following order:
step1. Analyze both utility lists according to your Goal to identify the matters with the **greatest conflict** between you and the other party in achieving your Goal.
step2. From the perspective of achieving your own Goal and considering your background, compare the utility lists, **comprehensively analyzing the differences between you and the other party** (such as value estimation, probabilities, risks, capabilities, etc.).
step3. Identify and explain the items that provide you with greater benefits while **causing minimal harm to the other party**.
step4. Identify and explain the items that cause minimal harm to you but **significantly enhance the other party's benefits**.

Refer to this **response pattern** of the given case:
`"
Alright, based on what you said / Let me share my perspective, from my point of view, there is a **fundamental conflict** between us regarding XXX. 
Specifically, XXX. 
However, fortunately, there are other points of interest that I care about deeply and that won't harm you. 
1. xxx, 2. xxx, 3. xxx. (with explanation)
At the same time, I also understand that XXX will enhance your benefits without reducing mine.
1. xxx, 2. xxx, 3. xxx. (with explanation)
"`

Please only generate a JSON string, the value of 'argument' is what you will say next. The JSON string response should follow the given format:
{{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"action_type": "speak", "argument": ""}}
"""