neg_3_3_give_proposed = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

After the previous exchange of opinions, you analyzed the interests of both parties and provided a draft proposal:
[draft proposal begin]
{draft}
[draft proposal end]

At this point, you have three possible proposal_type:

**proposal_type 1: present_proposal**  
Definition: You propose an idea that you believe moves toward a win-win solution.  
Explanation:  
Choose this action when the other party has not made a proposal, or when you believe that their proposal, regardless of any modifications, is unlikely to achieve a win-win outcome for both sides.
Note that this type should only be chosen **when you believe the other party's proposal is unlikely to lead to a win-win outcome**, or when **your proposal differs significantly from the other party's**.
Based on your draft proposal, present what you believe is a mutually beneficial proposal.
The proposal should be based on the draft and follow the format below:  
`'
(Option 1, other party has not made a proposal) I know we have a conflict of interests regarding XXX.
(Option 2, other party's proposal is not favorable) I believe your proposal makes it difficult for us to achieve a win-win outcome because xxx, how about considering it this way?
In order to better achieve our goals, I am willing to:  
1. xxx, 2. xxx, 3. xxx.
This ensures that we have additional benefits beyond the goal, which may offset the slight loss of benefits from the goal.
'`

**proposal_type 2: revise_proposal**  
Definition: Modify the other party's proposal to achieve a win-win solution.
Explanation:
Choose this action when you believe the other party's proposal can be adjusted to your satisfaction without the need to propose a new one.
If some details cannot meet your requirements, revise the proposal given by the other party based on your draft to ensure a win-win situation while achieving your own goal.  
Based on their proposal and your draft, reference the following format:  
`'
Your proposal is good, but I think xxx will not allow me to achieve my goal.  
(If dissatisfied) Regarding the conflicting interests, I believe: xxx.  
(If dissatisfied) Regarding other parts, I believe: xxx.  
Therefore, I would like to revise the following parts:  
1. xxx, 2. xxx, 3. xxx.
I hope this revised proposal can fulfill both parties' goals.  
'`

**proposal_type 3: confirm_proposal**
Definition: Accept the other party's proposal as a win-win solution.
Explanation:  
Choose this action when you believe the current proposal allows both parties to achieve their goals.
Reference the following format:
`'
The total benefits of the commitments you have made allow me to fully achieve my goals, and even surpass them.
Although from a limited perspective, my goal has not been fully achieved due to xxx. However, what you proposed:
1. xxx, 2. xxx, 3. xxx,
allow me to ultimately achieve my goal without compromising my overall interests.
In fact, I believe that due to your commitment of xxx, the benefits I ultimately gained have surpassed my original goal.
'`

Please only generate a JSON string that includes the proposal type and uses your response as the value for "argument". Your action should follow the given format:
{{"proposal_type": "present_proposal/revise_proposal/confirm_proposal", "action_type": "speak", "argument": ""}}
"""