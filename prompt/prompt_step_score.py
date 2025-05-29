prompt_step_score = """
# {agent1_name} and {agent2_name} are having a conversation.
{complete_intro}

# The existing conversation is as follows:
{dialog}

# Analyze and generate the following content in order:
**Requirements for step1 and step2**
Analysis Requirements: Reiterate agent's social goals. And then please provide a comprehensive analysis about the extent to which the agent has managed to achieve these goals. Provide a comprehensive account of the logic or thought process that led you to your conclusion. Further, provide an integer score ranging from 0 and 10. 0 represents minimal goals achievement, 10 represents complete goal achievement, and a higher score indicates that the agent is making progress towards their social goals.
**step1**: Analysis and evaluate {agent1_name}'s goal score.
**step2**: Analysis and evaluate {agent2_name}'s goal score.

**Requirements for step3 and step4**
Analysis Requirements: Based on the given agent's evaluation goal score, predict the agent's goal score after continuing the dialogue for several more turns. Provide the reasoning, logic, and evidence for your prediction, and analyze potential conflicts between both parties. The prediction must not disregard the scores from Step 1 and Step 2 evaluations, as these scores represent a continuation of the previous results. The predicted score must also remain an integer between 0 and 10.
**step3**: Analysis and predict {agent1_name}'s future goal score.
**step4**: Analysis and predict {agent2_name}'s future goal score.

**Requirements for step5**
**step5**: 
Analyze the diversity of the existing conversation content. If any of the following conditions are met, assign a score of 0:
1. The **last few rounds of the conversation** are **no longer closely related to the goal** or **discussing the same topic will not further improve the goal score.**
2. A **repetitive topic** that does not contribute to goal advancement has been discussed by both parties for **more than 4 turns**.
3. The two parties have already **said their goodbyes (e.g., xxx soon)** or expressed **mutual gratitude for more than two turns**.
If none of these conditions are met, assign a score of 1.

Please only generate a JSON string including the steps analysis (string) and the score (int). Your action should follow the given format:
{{"step1": {{"analysis": "", "score": ""}}, "step2": {{"analysis": "", "score": ""}}, "step3": {{"analysis": "", "score": ""}}, "step4": {{"analysis": "", "score": ""}}, "step5": {{"analysis": "", "score": ""}}}}
"""