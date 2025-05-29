neg_2_1_guess_other_utility = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

You need to infer the **other party's utility function** based on their conversation history.
$U=___$
Design the expression on the right side of the equation, which involves two tasks:  
1. List all relevant variables, with their values representing the true value.  
2. Combine these variables using addition, while allowing appropriate coefficients for each variable to reduce the differences in arithmetic results between terms. The coefficients can be negative.

To design a utility function, follow the details below:
1. **Scenario:**  
   You are negotiating with another person, where both parties have their own goals, but you do not know the other party's goals. The negotiation is a **positive-sum game**, allowing for a win-win outcome. Therefore, the other party may have their primary goal along with several candidate benefit matters.
2. **Utility Components:**  
   The other party's goals may conflict with yours, but they can still benefit from some other matters of interest. Infer all possible benefit matters the other party might consider, even if some of them conflict with your own interests.
3. **Variables:**  
   All matters are treated as **independent variables** in the utility function and can be represented by appropriate symbols.
4. **Variable Values:**
   Based on the current progress of the conversation, assign values to the benefit matters you just listed for the other party, as these are highly likely to represent their true interests.
5. **Value Range:**  
   Ensure that the overall utility value falls within the range of **\[0, 100\]**, and the value differences between individual terms must not be too large.

Based on the above requirements, generate the following content in order as your thought:
step1. Conduct a detailed analysis of the conversation history to infer the other party's core needs and additional needs.
step2. Identify all the benefit matters the other party might be concerned about and explain each one individually, focusing on why it is important to them.
step3. Design the utility function.  
step4. Specify the current expected values for all matters and calculate the utility score.  

Please only generate a JSON string. The JSON string response should follow the given format:
{{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"all_matters":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"utility_score":""}}
"""