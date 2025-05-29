neg_1_1_init_utility = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

You need to design a utility function based on **your goal** and **your previous conversations**.
$U=___$
Design the expression on the right side of the equation, which involves two tasks:  
1. List all relevant variables, with their values representing the true value.  
2. Combine these variables using addition, while allowing appropriate coefficients for each variable to reduce the differences in arithmetic results between terms. The coefficients can be negative.

To design a utility function, follow the details below:
1. **Scenario:**  
   You are negotiating with another person, where both parties have their own goals, but you do not know the other party's goals. The negotiation is a **positive-sum game**, allowing for a win-win outcome. Therefore, identifying more **alternative options** is particularly important.
2. **Utility Components:**  
   Assume that you cannot fully achieve your goals, but you may still consider yourself to have gained from other matters. Thus, you need to brainstorm and list as many matters as possible that you consider personally valuable. These can be a breakdown of your goals or other interests.
3. **Variables:**  
   All matters are treated as **independent variables** in the utility function and can be represented by appropriate symbols.
4. **Variable Values:**  
   Based on the current progress of the conversation, assign values to your goals and other benefit matters, representing the true values you believe align with your own interests.
5. **Value Range:**  
   Ensure that the overall utility value falls within the range of **\[0, 100\]**, and the value differences between individual terms must not be too large.

Based on the above requirements, generate the following content in order as your thought:
step1. Based on the existing conversation, carefully consider all of your own needs and summarize the needs of the other party.
step2. Identify all relevant matters and explain what each matter specifically entails and why it is important. Additionally, you should also include important content that was not mentioned in the previous conversation.
step3. Design the utility function.  
step4. Specify the current expected values for all matters and calculate the utility score.  

Please only generate a JSON string. The JSON string response should follow the given format:
{{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"all_matters":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"utility_score":""}}
"""