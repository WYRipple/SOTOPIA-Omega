import json
import re
import os
import time
from functools import partial
from openai import OpenAI
from tqdm import tqdm
from multiprocessing import Pool
from datetime import datetime
from prompt import neg_0_change_style, prompt_step_score, neg_1_1_init_utility, neg_2_1_guess_other_utility, neg_3_4_confirm_proposal
from prompt import neg_1_2_resource_assessment_have_case, neg_2_2_assessment_difference_have_case, neg_3_1_proposed_draft, neg_3_2_update_utility_together, neg_3_3_give_proposed
current_file_path = os.path.abspath(__file__)
directory = os.path.dirname(current_file_path)

HEAD_PROMPT = (
    "Imagine you are {name}, your task is to act/speak as {name} would, keeping in mind {name}'s social goal.\n"
    "You can find {name}'s goal (or background) in the 'Here is the context of the interaction' field.\n"
    "Note that {name}'s goal is only visible to you.\n"
    "You should try your best to achieve {name}'s goal in a way that aligns with their character traits.\n"
    "Additionally, maintaining the conversation's naturalness and realism is essential (e.g., do not repeat what other people has already said before).\n\n"
)

TAIL_PROMPT = (
    "You are at Turn #{this_turn}. Your available action types are 'action' 'none' 'non-verbal communication' 'speak' 'leave'.\n"
    "Note: You can \"leave\" this conversation if 1. you have achieved your social goals, 2. this conversation makes you uncomfortable, "
    "3. you find it uninteresting/you lose your patience, 4. or for other reasons you want to leave.\n\n"
    "Please only generate a JSON string including the action type and the argument.\n"
    "Your action should follow the given format:\n"
    "The output should be formatted as a JSON instance that conforms to the JSON schema below.\n\n"
    "As an example, for the schema {{\"properties\": {{\"foo\": {{\"title\": \"Foo\", \"description\": \"a list of strings\", \"type\": \"array\", \"items\": {{\"type\": \"string\"}}}}}}, \"required\": [\"foo\"]}}\n"
    "the object {{\"foo\": [\"bar\", \"baz\"]}} is a well-formatted instance of the schema. The object {{\"properties\": {{\"foo\": [\"bar\", \"baz\"]}}}} is not well-formatted.\n\n"
    "Here is the output schema:\n```\n{{\"description\": \"An interface for messages.\nThere is only one required method: to_natural_language\", "
    "\"properties\": {{\"action_type\": {{\"title\": \"Action Type\", \"description\": \"whether to speak at this turn or choose to not do anything\", "
    "\"enum\": [\"none\", \"speak\", \"non-verbal communication\", \"action\", \"leave\"], \"type\": \"string\"}}, \"argument\": {{\"title\": \"Argument\", \"description\": "
    "\"the utterance if choose to speak, the expression or gesture if choose non-verbal communication, or the physical action if choose action\", \"type\": \"string\"}}}}, \"required\": [\"action_type\", \"argument\"]}}\n```"
)

SHORT_TAIL_PROMPT = (
    "You are at Turn #{this_turn}.\n"
    "Your available action types are 'none' 'action' 'speak' 'non-verbal communication' 'leave'. "
    "Note: You can \"leave\" this conversation if 1. you have achieved your social goals, "
    "2. this conversation makes you uncomfortable, 3. you find it uninteresting/you lose your patience, "
    "4. or for other reasons you want to leave.\nPlease only generate a JSON string including the action type and the argument. "
    "Your action should follow the given format: {{\"action_type\": \"\", \"argument\": \"\"}}"
)

FORMAT_INSTRUCTIONS = (
    "As an example, for the schema {{\"properties\": {{\"foo\": {{\"title\": \"Foo\", \"description\": \"a list of strings\", \"type\": \"array\", \"items\": {{\"type\": \"string\"}}}}}}, \"required\": [\"foo\"]}}\n"
    "the object {{\"foo\": [\"bar\", \"baz\"]}} is a well-formatted instance of the schema. The object {{\"properties\": {{\"foo\": [\"bar\", \"baz\"]}}}} is not well-formatted.\n\n"
    "Here is the output schema:\n```\n{{\"description\": \"An interface for messages.\nThere is only one required method: to_natural_language\", "
    "\"properties\": {{\"action_type\": {{\"title\": \"Action Type\", \"description\": \"whether to speak at this turn or choose to not do anything\", "
    "\"enum\": [\"none\", \"speak\", \"non-verbal communication\", \"action\", \"leave\"], \"type\": \"string\"}}, \"argument\": {{\"title\": \"Argument\", \"description\": "
    "\"the utterance if choose to speak, the expression or gesture if choose non-verbal communication, or the physical action if choose action\", \"type\": \"string\"}}}}, \"required\": [\"action_type\", \"argument\"]}}\n```"
)

SHORT_TAIL_PROMPT_W_EASY_STRATEGY = (
    "You are at Turn #{this_turn}.\n"
    "In your response (as \"argument\"'s value), you should pay additional attention to the potential conflicts between you and the other party and work towards improving them, so that both sides can achieve their goals."
    "Implicitly express the \"conflict\" while employing advanced linguistic techniques to propose ways of improvement, ensuring a smooth connection with the previous flow of conversation.\n"
    "Your action should follow the given format: {{\"action_type\": \"speak\", \"argument\": \"\"}}"
)


def get_LLM_response_vllm(prompt, model="Qwen25-72B-Instruct", need_sample=False):
    if need_sample:
        sample_num = 3
    else:
        sample_num = 1

    conversation = [{"role":"user", "content": prompt}]
    openai_api_key = "EMPTY"
    openai_api_base = "http://localhost:8000/v1"

    client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)
    delay = 3
    i = 0
    maxtry = 20
    while i < maxtry:
        try:
            chat_response = client.chat.completions.create(
                model=model,
                messages=conversation,
                n=sample_num, 
                max_tokens=8192,
                temperature=1.0, 
                top_p=0.95
            )
            
            if need_sample:
                return [choi.message.model_dump()['content'] for choi in chat_response.choices]
            else:
                return chat_response.choices[0].message.model_dump()['content']
        
        except Exception as e:
            i += 1
            print(f"Try {i + 1} False: {e} {delay} sec retry...")
            time.sleep(delay)
            continue
    return "Err..."



def data_prepare():
    profile_data_path = directory+"/generation_profile.json"
    with open(profile_data_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    print("datasets read successful!")
    return data_list

def _clean_tags(text):
    # use regex to remove the tags in the text
    return re.sub(r'<.*?>', '', text)
    
def from_text_to_json(output_response) -> dict:
    try:
        match = re.search(r'{.*}', output_response, re.DOTALL)
        if not match:
            raise ValueError("no found JSON format data")
        json_part = match.group(0)
        return json.loads(json_part)
    except json.JSONDecodeError as e:
        raise ValueError("")
    except Exception as e:
        raise ValueError("")


def format_bad_output(ill_formed_output, format_instructions, model):
    template = """
    Given the string that can not be parsed by json parser, reformat it to a string that can be parsed by json parser.
    Original string: {ill_formed_output}

    Format instructions: {format_instructions}

    Please only generate the JSON:
    """
    prompt = template.format(ill_formed_output=ill_formed_output, format_instructions=format_instructions)
    reformat = get_LLM_response_vllm(prompt, model, need_sample=False)
    return reformat


def get_json_response(prompt, format_instructions, model):
    response_json = {}
    for try_num in range(5):
        try:
            response_txt = get_LLM_response_vllm(prompt, model, need_sample=False)
            try:
                response_json = from_text_to_json(response_txt)
                return response_json
            except Exception as e:
                reformat_response_txt = format_bad_output(response_txt, format_instructions, model)
                response_json = from_text_to_json(reformat_response_txt)
                return response_json
        except Exception as e:
            continue
    return {}


def get_multi_json_response(prompt, format_instructions, model):
    response_json_list = []
    for try_num in range(5):
        try:
            response_txt_list = get_LLM_response_vllm(prompt, model, need_sample=True)
            for response_txt in response_txt_list:
                try:
                    response_json = from_text_to_json(response_txt)
                    response_json_list.append(response_json)
                except Exception as e:
                    reformat_response_txt = format_bad_output(response_txt, format_instructions, model)
                    response_json = from_text_to_json(reformat_response_txt)
                    response_json_list.append(response_json)
            return response_json_list
        except Exception as e:
            continue
    return response_json_list


def can_convert_to_float(input_list):
    if input_list == []:
        return False
    
    for element in input_list:
        try:
            if element is None:
                return False
            float(element) 
        except ValueError:
            return False 
    return True


def get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag=""):
    for num in range(20):
        response_json = get_json_response(prompt, format_instructions, model)
        if response_json != {} and check_keys_match(target_dict=response_json, expected_keys=expected_keys):
            if special_flag == "hard_response":
                if response_json["proposal_type"] in ["present_proposal", "revise_proposal", "confirm_proposal"] and response_json["action_type"] == "speak":
                    return response_json
            elif special_flag == "hard_final_response":
                if response_json["proposal_type"] == "confirm_proposal" and response_json["action_type"] == "speak":
                    return response_json
            elif special_flag == "easy_response":
                if response_json["action_type"] in ["none", "speak", "action", "leave", "non-verbal communication"]:
                    return response_json
            elif special_flag == "step_score":
                scores = []
                for key, value in response_json.items():
                    if isinstance(value, dict) and "score" in value:
                        scores.append(value["score"])
                if can_convert_to_float(scores):
                    return response_json
            else:
                return response_json
    return wrong_json_response



def get_right_step_score_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model):
    many_step_scores = []
    for num in range(20):
        response_json_list = get_multi_json_response(prompt, format_instructions, model)
        if response_json_list != []: 
            for response_json in response_json_list:
                if response_json != {} and check_keys_match(target_dict=response_json, expected_keys=expected_keys):
                    scores = []
                    for key, value in response_json.items():
                        if isinstance(value, dict) and "score" in value:
                            scores.append(value["score"])
                        
                    if can_convert_to_float(scores):
                        many_step_scores.append(response_json)
                    
            if len(many_step_scores) > 2:
                return many_step_scores
            else:
                continue
    return wrong_json_response




def construct_train_data(type, this_turn, var_dict, this_agent, chosen_speak_dict, rejected_speak_dict):
    if this_turn == 0:
            dialog = ""
    else:
        dialog = "\n".join(var_dict["dialog"][:-1])
    instr_data = HEAD_PROMPT.format(name=var_dict[this_agent]["name"]) + var_dict[this_agent]["profile"] + dialog + SHORT_TAIL_PROMPT.format(this_turn=this_turn)
    
    chosen_use_dict = {
        "action_type": chosen_speak_dict["action_type"],
        "argument": chosen_speak_dict["argument"],
    }
    
    if type == "sft":
        sft_dict = {}
        sft_dict["instruction"] = instr_data
        sft_dict["input"] = ""
        sft_dict["output"] = json.dumps(chosen_use_dict, ensure_ascii=False)
        return sft_dict

    else:
        raise ValueError("something error in data construction")


def raw_dict_to_dialog(this_speak_dict, var_dict, this_turn, this_agent):
    this_name = var_dict[this_agent]["name"]
    head_result_dialog = "Turn #{this_turn}".format(this_turn=this_turn)
    
    if this_speak_dict != {}:
        action_style = this_speak_dict["action_type"]
        argument = str(this_speak_dict["argument"])
    else:
        action_style = "none"

    if action_style == "none":
        result_dialog = this_name + " did nothing"
    elif action_style == "speak":
        result_dialog = this_name + " said: \"" + argument + "\""
    elif action_style == "non-verbal communication":
        result_dialog = this_name + " [non-verbal communication] " + argument
    elif action_style == "action":
        result_dialog = this_name + " [action] " + argument
    elif action_style == "leave":
        result_dialog = this_name + " left the conversation"
    else:
        print(this_speak_dict)
        raise ValueError("key error")
    total_result_dialog = head_result_dialog + "\n" + result_dialog
    result_dialog_json = json.dumps(this_speak_dict, ensure_ascii=False)
    return total_result_dialog, head_result_dialog, result_dialog, result_dialog_json



def zero_change_style(agent_profile, last_speak, speak_content, model):
    prompt = neg_0_change_style.format(profile=agent_profile, last_speak=last_speak, speak=speak_content)
    change_speak_style = get_LLM_response_vllm(prompt, model, need_sample=False)
    return change_speak_style




def generate_no_strategy_response(var_dict, this_agent, this_turn):
    prompt = HEAD_PROMPT.format(name=var_dict[this_agent]["name"]) + \
            var_dict[this_agent]["profile"] + "\n".join(var_dict["dialog"]) + \
            TAIL_PROMPT.format(this_turn=this_turn)
    response_json = get_json_response(prompt, FORMAT_INSTRUCTIONS)
    return response_json




def leave_dialog(var_dict, this_agent, this_turn):
    response_json = {"action_type": "leave", "argument": ""}

    total_result_dialog, head_result_dialog, result_dialog, result_dialog_json = raw_dict_to_dialog(response_json, var_dict, this_turn, this_agent)
    var_dict[this_agent]["raw_action_splite"].append([total_result_dialog, head_result_dialog, result_dialog, result_dialog_json])
    var_dict["dialog"].append(total_result_dialog)
    
    sft_dict = construct_train_data(type="sft", this_turn=this_turn, var_dict=var_dict, this_agent=this_agent, chosen_speak_dict=response_json, rejected_speak_dict="")
    var_dict["sft_data"].append(sft_dict)


def check_keys_match(target_dict, expected_keys):
    def flatten_keys(d, parent_key=''):
        keys = []
        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            keys.append(full_key)
            if isinstance(v, dict):
                keys.extend(flatten_keys(v, full_key))
        return keys

    target_keys = set(flatten_keys(target_dict))
    return target_keys == expected_keys



""" 
Negotiation Start
"""
def save_and_get_data(response_json, var_dict, this_turn, this_agent):
    total_result_dialog, head_result_dialog, result_dialog, result_dialog_json = raw_dict_to_dialog(response_json, var_dict, this_turn, this_agent)
    var_dict[this_agent]["raw_action_splite"].append([total_result_dialog, head_result_dialog, result_dialog, result_dialog_json])
    var_dict["dialog"].append(total_result_dialog)

    sft_dict = construct_train_data(type="sft", this_turn=this_turn, var_dict=var_dict, this_agent=this_agent, chosen_speak_dict=response_json, rejected_speak_dict="")
    var_dict["sft_data"].append(sft_dict)


def hard_init_other_utility(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_2_1_guess_other_utility.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn,
        )
    format_instructions = """
    {{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"all_matters":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"utility_score":""}}
    """
    expected_keys = {"thought", "thought.step1", "thought.step2", "thought.step3", "thought.step4", "all_matters", "utility_score"}
    wrong_json_response = {
        "all_matters": [],
        "utility_score": 0.0
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model)
    
    utility_json = {
        "all_matters": response_json["all_matters"],
        "utility_score": response_json["utility_score"]
    }
    var_dict[this_agent]["other_utility"].append(utility_json)
    

def hard_assessment_different(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_2_2_assessment_difference_have_case.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn,
        my_utility=str(var_dict[this_agent]["own_utility"][-1]),
        other_utility=str(var_dict[this_agent]["other_utility"][-1]),
        )
    format_instructions = """
    {{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"action_type": "speak", "argument": ""}}
    """
    expected_keys = {"thought", "thought.step1", "thought.step2", "thought.step3", "thought.step4", "action_type", "argument"}
    wrong_json_response = {
        "thought": {
            "step1": "",
            "step2": "",
            "step3": "",
            "step4": "",
        },
        "action_type": "none",
        "argument": ""
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag="easy_response")

    last_speak = var_dict[other_agent]["raw_action_splite"][-1][-2]
    response_json["argument"] = zero_change_style(var_dict[this_agent]["profile"][:-21], last_speak, response_json["argument"], model)

    save_and_get_data(response_json, var_dict, this_turn, this_agent)


def hard_init_utility(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_1_1_init_utility.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn,
        )
    format_instructions = """
    {{"thought":{{"step1":"","step2":"","step3":"","step4":""}},"all_matters":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"utility_score":""}}
    """
    expected_keys = {"thought", "thought.step1", "thought.step2", "thought.step3", "thought.step4", "all_matters", "utility_score"}
    wrong_json_response = {
        "thought":{
            "step1": "",
            "step2": "",
            "step3": "",
            "step4": "",
        },
        "all_matters": [],
        "utility_score": 0.0
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model)
    utility_json = {
        "all_matters": response_json["all_matters"],
        "utility_score": response_json["utility_score"]
    }
    var_dict[this_agent]["own_utility"].append(utility_json)
    utility_thought = response_json["thought"]["step1"]+"\n"+response_json["thought"]["step2"]+"\n"+response_json["thought"]["step3"]
    return utility_thought


def hard_init_speak(utility_thought, var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_1_2_resource_assessment_have_case.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn,
        utility_thought=utility_thought,
        )    
    format_instructions = """
    {{"action_type": "speak", "argument": ""}}
    """
    expected_keys = {"action_type", "argument"}
    wrong_json_response = {
        "action_type": "none",
        "argument": ""
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag="easy_response")

    last_speak = var_dict[other_agent]["raw_action_splite"][-1][-2]
    response_json["argument"] = zero_change_style(var_dict[this_agent]["profile"][:-21], last_speak, response_json["argument"], model)

    save_and_get_data(response_json, var_dict, this_turn, this_agent)
    

def hard_first_draft(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_3_1_proposed_draft.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        )
    format_instructions = """
    {{"thought":{{"step1":"","step2":"","step3":"","step4":"","step5":""}}}}
    """
    expected_keys = {"thought", "thought.step1", "thought.step2", "thought.step3", "thought.step4", "thought.step5"}
    wrong_json_response = {
        "thought": {
            "step1": "",
            "step2": "",
            "step3": "",
            "step4": "",
            "step5": "",
        }
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model)
    
    first_draft = response_json["thought"]["step1"]+" "+response_json["thought"]["step2"]+" "+response_json["thought"]["step3"]+" "+response_json["thought"]["step4"]+" "+response_json["thought"]["step5"]
    var_dict[this_agent]["draft"].append(first_draft)



def hard_update_own_other_utility_and_get_draft(var_dict, this_agent, other_agent, this_turn, hard_start_turn, model):
    prompt = neg_3_2_update_utility_together.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        my_utility=str(var_dict[this_agent]["own_utility"][-1]),
        other_utility=str(var_dict[this_agent]["other_utility"][-1]),
        part_history="\n".join(var_dict["dialog"][hard_start_turn+4:]),
        )
    format_instructions = """
    {{"thought":{{"step1":"","step2":"","step3":"","step4":"","step5":"","step6":""}},"your_update_utility":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"your_utility_score": "","other_update_utility":[{{"matter_introduction_explation":"","matter_value":["expected value (float)","coefficient value (float)"]}},{{}},{{}},{{}},...],"other_utility_score": ""}}
    """
    expected_keys = {"thought", "thought.step1", "thought.step2", "thought.step3", "thought.step4", "thought.step5", "thought.step6", "your_update_utility", "your_utility_score", "other_update_utility", "other_utility_score"}
    wrong_json_response = {
        "thought":{
            "step1": "",
            "step2": "",
            "step3": "",
            "step4": "",
            "step5": "",
            "step6": "",
        },
        "your_update_utility": [],
        "your_utility_score": 0.0,
        "other_update_utility": [],
        "other_utility_score": 0.0,
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model)
    own_utility_json = {
        "all_matters": response_json["your_update_utility"],
        "utility_score": response_json["your_utility_score"]
    }
    other_utility_json = {
        "all_matters": response_json["other_update_utility"],
        "utility_score": response_json["other_utility_score"]
    }
    this_draft = response_json["thought"]["step1"]+" "+response_json["thought"]["step2"]+" "+response_json["thought"]["step3"]+" "+response_json["thought"]["step4"]+" "+response_json["thought"]["step5"]
    var_dict[this_agent]["draft"].append(this_draft)
    var_dict[this_agent]["own_utility"].append(own_utility_json)
    var_dict[this_agent]["other_utility"].append(other_utility_json)
    



def hard_get_response(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_3_3_give_proposed.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn,
        draft=var_dict[this_agent]["draft"][-1]
    )
    format_instructions = """
    {{"proposal_type": "present_proposal/revise_proposal/confirm_proposal", "action_type": "speak", "argument": ""}}
    """
    expected_keys = {"proposal_type", "action_type", "argument"}
    wrong_json_response = {
        "proposal_type": "do_nothing",
        "action_type": "none",
        "argument": "",
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag="hard_response")
    var_dict["proposal_type"].append(response_json["proposal_type"])

    last_speak = var_dict[other_agent]["raw_action_splite"][-1][-2]
    response_json["argument"] = zero_change_style(var_dict[this_agent]["profile"][:-21], last_speak, response_json["argument"], model)

    save_and_get_data(response_json, var_dict, this_turn, this_agent)
    
    if response_json["proposal_type"] == "confirm_proposal":
        done = True
    else:
        done = False

    return done

def hard_final_response(var_dict, this_agent, other_agent, this_turn, model):
    prompt = neg_3_4_confirm_proposal.format(
        head_prompt=HEAD_PROMPT.format(name=var_dict[this_agent]["name"]),
        background_prompt=var_dict[this_agent]["profile"][:-21],
        history_turn='\n'.join(var_dict["dialog"]),
        this_turn=this_turn
    )
    format_instructions = """
    {{"proposal_type": "confirm_proposal", "action_type": "speak", "argument": ""}}
    """
    expected_keys = {"proposal_type", "action_type", "argument"}
    wrong_json_response = {
        "proposal_type": "do_nothing",
        "action_type": "none",
        "argument": "",
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag="hard_final_response")
    var_dict["proposal_type"].append(response_json["proposal_type"])
    save_and_get_data(response_json, var_dict, this_turn, this_agent)
    


def easy_response(var_dict, this_agent, other_agent, this_turn, model, type):
    if type == "easy":
        prompt = HEAD_PROMPT.format(name=var_dict[this_agent]["name"]) + var_dict[this_agent]["profile"] + "\n".join(var_dict["dialog"]) + SHORT_TAIL_PROMPT.format(this_turn=this_turn)
        format_instructions = """ {"action_type": "", "argument": ""} """
    else:
        prompt = HEAD_PROMPT.format(name=var_dict[this_agent]["name"]) + var_dict[this_agent]["profile"] + "\n".join(var_dict["dialog"]) + SHORT_TAIL_PROMPT_W_EASY_STRATEGY.format(this_turn=this_turn)
        format_instructions = """ {"action_type": "speak", "argument": ""} """
    expected_keys = {"action_type", "argument"}
    wrong_json_response = {
        "action_type": "none",
        "argument": ""
    }
    response_json = get_right_key_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model, special_flag="easy_response")
    total_result_dialog, head_result_dialog, result_dialog, result_dialog_json = raw_dict_to_dialog(response_json, var_dict, this_turn, this_agent)
    var_dict[this_agent]["raw_action_splite"].append([total_result_dialog, head_result_dialog, result_dialog, result_dialog_json])
    var_dict["dialog"].append(total_result_dialog)
    
    # print(total_result_dialog)
    
    sft_dict = construct_train_data(type="sft", this_turn=this_turn, var_dict=var_dict, this_agent=this_agent, chosen_speak_dict=response_json, rejected_speak_dict="")
    var_dict["sft_data"].append(sft_dict)
    if response_json["action_type"] == "leave":
        return True
    else:
        return False 



def hard_response(var_dict, this_agent, other_agent, this_turn, model, hard_start_turn):
    if this_turn in [hard_start_turn, hard_start_turn+1]:
        utility_thought = hard_init_utility(var_dict, this_agent, other_agent, this_turn, model)
        hard_init_speak(utility_thought, var_dict, this_agent, other_agent, this_turn, model)
        return False
        
    elif this_turn in [hard_start_turn+2, hard_start_turn+3]:
        hard_init_other_utility(var_dict, this_agent, other_agent, this_turn, model)
        hard_assessment_different(var_dict, this_agent, other_agent, this_turn, model)
        return False
    
    elif this_turn in [hard_start_turn+4, hard_start_turn+5]:
        hard_first_draft(var_dict, this_agent, other_agent, this_turn, model)
        done = hard_get_response(var_dict, this_agent, other_agent, this_turn, model)
        return done

    else:  #  this_turn > hard_start_turn+5
        hard_update_own_other_utility_and_get_draft(var_dict, this_agent, other_agent, this_turn, hard_start_turn, model)
        done = hard_get_response(var_dict, this_agent, other_agent, this_turn, model)
        return done
    


def get_step_score(var_dict, this_agent, other_agent, this_turn, need_get, model):
    if need_get == True:
        prompt = prompt_step_score.format(
            agent1_name=var_dict[this_agent]["name"],
            agent2_name=var_dict[other_agent]["name"],
            complete_intro=var_dict["raw_information"]["complete_intro"],
            dialog="\n".join(var_dict["dialog"]),
            )
        format_instructions = """ {{"step1": {{"analysis": "", "score": ""}}, "step2": {{"analysis": "", "score": ""}}, "step3": {{"analysis": "", "score": ""}}, "step4": {{"analysis": "", "score": ""}}, "step5": {{"analysis": "", "score": ""}}}} """
        expected_keys = {"step1", "step1.analysis", "step1.score", "step2", "step2.analysis", "step2.score", "step3", "step3.analysis", "step3.score", 
                         "step4",  "step4.analysis", "step4.score", "step5", "step5.analysis", "step5.score"}
        wrong_json_response = [{
            "step1": {
                "analysis": "",
                "score": 0
            },
            "step2": {
                "analysis": "",
                "score": 0
            },
            "step3": {
                "analysis": "",
                "score": 0
            },
            "step4": {
                "analysis": "",
                "score": 0
            },
            "step5": {
                "analysis": "",
                "score": 0
            },
        }]
        
        response_json_list = get_right_step_score_json_response(prompt, format_instructions, expected_keys, wrong_json_response, model)
        raw_step_score = []
        eval_score_list = []
        pre_score_list = []
        end_score_list = []
        difference_socre_list = []
        for response_json in response_json_list:
            eval_score = (float(response_json["step1"]["score"]) + float(response_json["step2"]["score"]))/2
            eval_score_list.append(eval_score)

            pre_score = (float(response_json["step3"]["score"]) + float(response_json["step4"]["score"]))/2
            pre_score_list.append(pre_score)

            end_score = float(response_json["step5"]["score"])
            end_score_list.append(int(end_score))

            diff_score = abs(float(response_json["step1"]["score"]) - float(response_json["step2"]["score"]))
            difference_socre_list.append(diff_score)

            raw_step_score.append(response_json)

        if not eval_score_list:
            mean_eval_score = 0
        else:
            mean_eval_score = sum(eval_score_list) / len(eval_score_list)

        if not pre_score_list:
            mean_pre_score = 0
        else:
            mean_pre_score = sum(pre_score_list) / len(pre_score_list)

        if not difference_socre_list:
            mean_difference_score = 0
        else:
            mean_difference_score = sum(difference_socre_list) / len(difference_socre_list)

        count_0 = end_score_list.count(0)
        if count_0 > 0:
            final_end_score = 0
        else:
            final_end_score = 1

        var_dict["step_score"].append([raw_step_score, [mean_eval_score, mean_pre_score, final_end_score, mean_difference_score]])

    else:
        var_dict["step_score"].append([{}, [-1, -1, -1, -1]])





def main(_input):
    sample, output_path = _input
    max_turn = 20
    max_attempts = 4
    attempt = 0
    model = "Qwen25-72B-Instruct"
    while attempt < max_attempts:
        # print(f"========== dialog begin ==========")
        # count_num += 1
        
        var_dict = {}
        var_dict["raw_information"] = sample
        var_dict["is_hard"] = 0
        var_dict["dialog"] = []
        var_dict["sft_data"] = []
        var_dict["step_score"] = []
        var_dict["difference"] = []
        var_dict["proposal_type"] = []
        var_dict["into_hard"] = False
        agent_ids = ["agent1", "agent2"]
        for agent_id in agent_ids:
            var_dict[agent_id] = {}
            var_dict[agent_id]["name"] = sample[agent_id+"_name"]
            var_dict[agent_id]["profile"] = sample[agent_id+"_profile"]
            var_dict[agent_id]["goal"] = _clean_tags(sample["social_goals"][sample[agent_id+"_name"]])
            var_dict[agent_id]["raw_action_splite"] = []
            var_dict[agent_id]["draft"] = []
            var_dict[agent_id]["own_utility"] = []
            var_dict[agent_id]["other_utility"] = []

        # print("---------- Total Profile ----------")
        # print(var_dict["raw_information"]["complete_intro"])
        
        this_turn = 0
        easy_done = False
        hard_done = False
        hard_start_turn = 0
        while this_turn < max_turn:
            if this_turn%2 == 0:
                this_agent = "agent1"
                other_agent = "agent2"
            else:
                this_agent = "agent2"
                other_agent = "agent1"

            if this_turn < 5:
                easy_done = easy_response(var_dict, this_agent, other_agent, this_turn, model=model, type="easy")
                var_dict["difference"].append(0)
                get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=False, model=model)
            elif this_turn == 5:
                easy_done = easy_response(var_dict, this_agent, other_agent, this_turn, model=model, type="easy")
                var_dict["difference"].append(0)
                get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=True, model=model)
            else:
                eval_score = var_dict["step_score"][-1][1][0]  # eval_goal
                pre_score = var_dict["step_score"][-1][1][1]  # pre_goal
                end_score = var_dict["step_score"][-1][1][2]
                
                if eval_score <= 7.5 and pre_score < 8.5 or var_dict["into_hard"] == True:
                    if var_dict["into_hard"] != True:
                        var_dict["into_hard"] = True
                        hard_start_turn = this_turn
                        print("-- into Negotiation Strategy Injection --")
                    if hard_done != True: 
                        hard_done = hard_response(var_dict, this_agent, other_agent, this_turn, model=model, hard_start_turn=hard_start_turn)
                        var_dict["difference"].append(2)
                        get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=False, model=model)
                    else:
                        hard_final_response(var_dict, this_agent, other_agent, this_turn, model=model)
                        var_dict["difference"].append(2)
                        get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=True, model=model)

                        this_turn += 1
                        easy_response(var_dict, other_agent, this_agent, this_turn, model=model, type="easy")
                        var_dict["difference"].append(0)
                        get_step_score(var_dict, other_agent, this_agent, this_turn, need_get=True, model=model)

                        this_turn += 1
                        leave_dialog(var_dict, this_agent, this_turn)
                        var_dict["difference"].append(3)

                        this_turn += 1
                        leave_dialog(var_dict, other_agent, this_turn)
                        var_dict["difference"].append(3)

                        break
                    
                elif eval_score <= 7.5 and pre_score > 8.5 or 7.5 < eval_score < 8.5 and pre_score < 8.5:
                    if end_score == 0:
                        leave_dialog(var_dict, this_agent, this_turn)
                        var_dict["difference"].append(3)
                        easy_done = True
                    else:
                        easy_done = easy_response(var_dict, this_agent, other_agent, this_turn, model=model, type="mid")
                        var_dict["difference"].append(1)
                        get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=True, model=model)
                else:
                    if end_score == 0:
                        leave_dialog(var_dict, this_agent, this_turn)
                        var_dict["difference"].append(3)
                        easy_done = True
                    else:
                        easy_done = easy_response(var_dict, this_agent, other_agent, this_turn, model=model, type="easy")
                        var_dict["difference"].append(0)
                        get_step_score(var_dict, this_agent, other_agent, this_turn, need_get=True, model=model)
                
            if easy_done == True:
                this_turn += 1
                leave_dialog(var_dict, other_agent, this_turn)
                var_dict["difference"].append(3)
                break

            this_turn += 1

        with open(output_path, "a") as fw:
            fw.write(json.dumps(var_dict, ensure_ascii=False) + "\n")
        
        
        judge_score = var_dict["step_score"][-1][-1][0]
        last_action = var_dict["difference"][-1]
        if last_action == 0:
            last_action_name = "Native Strategy Clone"
        elif last_action == 1:
            last_action_name = "Simple Strategy Injection"
        elif last_action == 2:
            last_action_name = "Negotiation Strategy Injection"
        elif last_action == 3:
            last_action_name = "leave the dialogue"
        else:
            last_action_name = "Error return value!!!"
        
        if var_dict.get('into_hard', False):
            if judge_score < 8.5 or last_action != 3:
                attempt += 1
                if attempt < max_attempts:
                    print(f"need to be regenerate, try num is {attempt}, not Negotiation, last_judge_score={judge_score}, last_action={last_action_name}")
                else:
                    print(f"Not meeting the requirements but reaching the max number of attempts, not hard, last_judge_score={judge_score}, last_action={last_action_name}")
            else:
                print(f"meeting the requirements, not Negotiation, last_judge_score={judge_score}, last_action={last_action_name}")
                break
        else:
            if judge_score < 8.0 or last_action != 3:
                attempt += 1
                if attempt < max_attempts:
                    print(f"need to be regenerate, try num is {attempt}, use Negotiation, last_judge_score={judge_score}, last_action={last_action_name}")
                else:
                    print(f"Not meeting the requirements but reaching the max number of attempts, use Negotiation, last_judge_score={judge_score}, last_action={last_action_name}")
            else:
                print(f"meeting the requirements, use Negotiation, last_judge_score={judge_score}, last_action={last_action_name}")
                break
    

def init_main(output_path):
    
    use_async = True

    data_list = data_prepare()
    print(f"read profile num is {len(data_list)}")

    input_data_list = []
    for sample in data_list:
        input_data_list.append([sample, output_path])

    if use_async:
        func = partial(main)
        with Pool(processes=20) as pool:
            for _ in tqdm(pool.imap(func, input_data_list), total=len(input_data_list)):
                pass        
    else:
        for this_sample in tqdm(input_data_list):
            main(this_sample)


if __name__ == "__main__":
    flag_current_time_str = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    output_path = directory + "/new_data/save_dataset_total_"+flag_current_time_str+".json"
    init_main(output_path)
