neg_3_2_update_utility_together = """
{head_prompt}

{background_prompt}

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

In the previous round of negotiations, the other party did not accept your proposal.
The final conversation history is as follows, with the last Turn being the response from the other party to your most recent proposal:
{part_history} 

Follow these steps as your thought:
step1. Analyze why the other party did not accept your proposed demands, referring to both parties' utility lists, and think deeply about which specific aspects have harmed the other party's interests.
step2. Based on the analysis in step1, try to find better or improved aspects that can generate additional value for the other party without harming your own interests.  
step3. Analyze what new demands the other party has made. Referring to your utility list, carefully analyze whether these demands harm your interests.
step4. 
    Based on the analysis in step3, 
    if the other party's demands do not harm your interests, try to expand the value of the demands, as this can provide more benefits to the other party; 
    if it harms your interests, try to find a clever improvement that satisfies the other party's needs without harming your own interests.
step5. Summarize how all the possible improvements proposed above enhance the other party's overall benefits, thereby enabling the other party to achieve the goal.
step6. Based on the above analysis, explain how to update both utility lists while keeping untouched items unchanged. Updates can include **adding** or **removing** matters or **adjusting weights and coefficients**.  

Please only generate a JSON string. The JSON string response should follow the given format:
{{"thought":{{"step1":"","step2":"","step3":"","step4":"","step5":"","step6":""}},"your_update_utility":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"your_utility_score": "","other_update_utility":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"other_utility_score": ""}}
"""