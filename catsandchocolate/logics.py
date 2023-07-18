import json
import jsonschema
from catsandchocolate import parameters
import openai


def generate_items(param: parameters.GenerateItemsParameters):
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "number",
                            "description": "連番",
                        },
                        "name": {
                            "type": "string",
                            "description": "物品名"
                        }
                    },
                    "required": ["id", "name"],
                    "minItems": param.count,
                    "maxItems": param.count,
                }
            }
        },
        "required": ["items"]
    }
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content":
                     f"「{param.title}」から連想される物品を{param.count}個生成してください。"}
                ],
                functions=[{
                    "name": "generateItems",
                    "description": "生成した物品を返す",
                    "parameters": schema
                }],
                function_call={"name": "generateItems"})
            message = response['choices'][0]['message']  # type: ignore
            args = message['function_call']['arguments']
            jsonschema.validate(json.loads(args), schema)
            return args
        except:
            continue


def generate_events(param: parameters.GenerateEventsParameters):
    schema = {
        "type": "object",
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "number",
                            "description": "連番",
                        },
                        "summary": {
                            "type": "string",
                            "description": "ピンチのシチュエーションを10文字以内で要約"
                        },
                        "event": {
                            "type": "string",
                            "description": "ピンチのシチュエーションを具体的に書く"
                        }
                    },
                    "required": ["id", "summary", "event"],
                    "minItems": param.count,
                    "maxItems": param.count,
                }
            }
        },
        "required": ["events"]
    }
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content":
                     f"「{param.title}」で発生し得るピンチのシチュエーションを{param.count}個生成してください。それぞれに10文字以内の要約を付加してください。"}
                ],
                functions=[{
                    "name": "generateEvents",
                    "description": "生成したイベントを返す",
                    "parameters": schema
                }],
                function_call={"name": "generateEvents"})
            message = response['choices'][0]['message']  # type: ignore
            args = message['function_call']['arguments']
            jsonschema.validate(json.loads(args), schema)
            return args
        except:
            continue


def evaluate_solution(param: parameters.EvaluateSolutionParameters):
    schema = {
        "type": "object",
        "properties": {
            "appropriate_score": {
                "type": "number",
                "description": "score that evaluates whether the solution to the pinch can be solved with that solution",
            },
            "humorous_score": {
                "type": "number",
                "description": "score is based on whether the solution to the pinch is humorous or not",
            },
            "comment": {
                "type": "string",
                "description": "comments on your impression in Japanese",
            },
            "tension": {
                "type": "number",
                "description": "Quantify whether the tension in the comments on your impression is positive or negative.",
            }
        },
        "required": ["appropriate_score", "humorous_score", "comment", "tension"]
    }
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": '''
                     You are a strict judge.
                     You strictly evaluate the adequacy of the proposed solution to the pinch point on a 100-point scale.
                     You also receive a score out of 100 wheather the solution is humorous.
                     Then, if either adequacy or humor is met, the impression of the solution is commented on favorably, without mentioning whether the other is not met.'''},
                    {"role": "user", "content":
                     f'''situation: {param.title}
                     pinch: {param.event}
                     solution: {param.solution}
                     '''}
                ],
                functions=[{
                    "name": "evaluateSolution",
                    "description": "evaluate the solution to the pinch",
                    "parameters": schema
                }],
                function_call={"name": "evaluateSolution"})
            msg = response['choices'][0]['message']  # type: ignore
            args = msg['function_call']['arguments']
            jsonschema.validate(json.loads(args), schema)
            return args
        except:
            continue


def find_solution(param: parameters.FindSolutionParameters):
    schema = {
        "type": "object",
        "properties": {
            "used_items": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "使用する物品名"
                },
                "description": "行動で使用する物品",
                "minItems": param.number_to_use,
                "maxItems": param.number_to_use,
            },
            "solution": {
                "type": "string",
                "description": "行動プランを物語仕立てで書く",
            },
        },
        "required": ["used_items", "solution"]
    }
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": '''
                     A: ピンチを切り抜ける行動プランを出す。ただし行動プランは以下の条件に従うこと。
                    ・指示された物品の中から、指示された種類の数だけ使用していること。指示された種類の数より使った物品の種類が多かったり、少なかったりした場合、誰かが死にます。
                    ・使用を決めた物品と、ピンチの状況から当然存在する物品だけを用いて実行可能な行動であること
                    ・ピンチの打開につながる行動が好ましい
                    ・ユーモラスな行動であればなお良い
                    ・行動プランは具体的かつ詳細に、物語仕立てで書いてください
                    またBがNGを出した場合、全く新しい別の行動プランを出すこと。
                    
                    B: Aの行動プランが以下の条件に従っているかチェックし、「OK」または「NG」を返す。
                    ・ピンチの状況から当然存在する物品の他には、指定された数の物品しか使用していないこと。
                    ・ピンチの状況から当然存在する物品と、指示された物品しか使用していないこと。
                    
                    BがOKを出すまで、Aは行動プランを出し続けてください。
                    最終的にBがOKを出した行動プランを出力してください。
                    '''},
                    {"role": "user", "content":
                     f'''シチュエーション: {param.title}
                     ピンチ: {param.event}
                     物品: {"、".join(param.items)}
                     物品の中から{param.number_to_use}つだけを用いてください。
                     '''}
                ],
                functions=[{
                    "name": "decidedAction",
                    "description": "行動プラン",
                    "parameters": schema
                }],
                function_call={"name": "decidedAction"})
            message = response['choices'][0]['message']  # type: ignore
            args = message['function_call']['arguments']
            jsonschema.validate(json.loads(args), schema)
            return args
        except:
            continue
