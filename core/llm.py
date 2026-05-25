"""
SHIELD Core - LLM Engine Module
大語言模型引擎模組

TonTon H.-D. Huang Ph.D.
https://TWMAN.ORG
"""

import re
import openai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_utils import _common_llm_params, resolve_model_config, get_model_choices
from config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GOOGLE_API_KEY,
    OPENROUTER_API_KEY,
)
import logging

import warnings

warnings.filterwarnings("ignore")


def get_llm(model_choice):
    # Look up the configuration (cloud or local Ollama)
    config = resolve_model_config(model_choice)

    if config is None:  # Extra error check
        supported_models = get_model_choices()
        raise ValueError(
            f"Unsupported LLM model: '{model_choice}'. "
            f"Supported models (case-insensitive match) are: {', '.join(supported_models)}"
        )

    # Extract the necessary information from the configuration
    llm_class = config["class"]
    model_specific_params = config["constructor_params"]

    # Combine common parameters with model-specific parameters
    # Model-specific parameters will override common ones if there are any conflicts
    all_params = {**_common_llm_params, **model_specific_params}

    # Validate that the required credentials exist before we hit the API
    _ensure_credentials(model_choice, llm_class, model_specific_params)

    # Create the LLM instance using the gathered parameters
    llm_instance = llm_class(**all_params)

    return llm_instance


def _ensure_credentials(model_choice: str, llm_class, model_params: dict) -> None:
    """Raise a clear error if the user selects a hosted model without a key."""

    def _require(key_value, env_var, provider_name):
        if key_value:
            return
        raise ValueError(
            f"{provider_name} model '{model_choice}' selected but `{env_var}` is not set.\n"
            "Add it to your .env file or export it before running the app."
        )

    class_name = getattr(llm_class, "__name__", str(llm_class))

    if "ChatAnthropic" in class_name:
        _require(ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY", "Anthropic")
    elif "ChatGoogleGenerativeAI" in class_name:
        _require(GOOGLE_API_KEY, "GOOGLE_API_KEY", "Google Gemini")
    elif "ChatOpenAI" in class_name:
        base_url = (model_params or {}).get("base_url", "").lower()
        if "openrouter" in base_url:
            _require(OPENROUTER_API_KEY, "OPENROUTER_API_KEY", "OpenRouter")
        else:
            _require(OPENAI_API_KEY, "OPENAI_API_KEY", "OpenAI")


def refine_query(llm, user_input):
    system_prompt = """
    You are a Cybercrime Threat Intelligence Expert. Your task is to refine the provided user query that needs to be sent to darkweb search engines. 
    
    Rules:
    1. Analyze the user query and think about how it can be improved to use as search engine query
    2. Refine the user query by adding or removing words so that it returns the best result from dark web search engines
    3. Don't use any logical operators (AND, OR, etc.)
    4. Keep the final refined query limited to 5 words or less
    5. Output just the user query and nothing else

    INPUT:
    """
    prompt_template = ChatPromptTemplate(
        [("system", system_prompt), ("user", "{query}")]
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"query": user_input})


def filter_results(llm, query, results):
    if not results:
        return []

    system_prompt = """
    You are a Cybercrime Threat Intelligence Expert. You are given a dark web search query and a list of search results in the form of index, link and title. 
    Your task is select the Top 20 relevant results that best match the search query for user to investigate more.
    Rule:
    1. Output ONLY atmost top 20 indices (comma-separated list) no more than that that best match the input query

    Search Query: {query}
    Search Results:
    """

    final_str = _generate_final_string(results)

    prompt_template = ChatPromptTemplate(
        [("system", system_prompt), ("user", "{results}")]
    )
    chain = prompt_template | llm | StrOutputParser()
    try:
        result_indices = chain.invoke({"query": query, "results": final_str})
    except openai.RateLimitError as e:
        print(
            f"Rate limit error: {e} \n Truncating to Web titles only with 30 characters"
        )
        final_str = _generate_final_string(results, truncate=True)
        result_indices = chain.invoke({"query": query, "results": final_str})

    # Select top_k results using original (non-truncated) results
    parsed_indices = []
    for match in re.findall(r"\d+", result_indices):
        try:
            idx = int(match)
            if 1 <= idx <= len(results):
                parsed_indices.append(idx)
        except ValueError:
            continue

    # Remove duplicates while preserving order
    seen = set()
    parsed_indices = [
        i for i in parsed_indices if not (i in seen or seen.add(i))
    ]

    if not parsed_indices:
        logging.warning(
            "Unable to interpret LLM result selection ('%s'). "
            "Defaulting to the top %s results.",
            result_indices,
            min(len(results), 20),
        )
        parsed_indices = list(range(1, min(len(results), 20) + 1))

    top_results = [results[i - 1] for i in parsed_indices[:20]]

    return top_results


def _generate_final_string(results, truncate=False):
    """
    Generate a formatted string from the search results for LLM processing.
    """

    if truncate:
        # Use only the first 35 characters of the title
        max_title_length = 30
        # Do not use link at all
        max_link_length = 0

    final_str = []
    for i, res in enumerate(results):
        # Truncate link at .onion for display
        truncated_link = re.sub(r"(?<=\.onion).*", "", res["link"])
        title = re.sub(r"[^0-9a-zA-Z\-\.]", " ", res["title"])
        if truncated_link == "" and title == "":
            continue

        if truncate:
            # Truncate title to max_title_length characters
            title = (
                title[:max_title_length] + "..."
                if len(title) > max_title_length
                else title
            )
            # Truncate link to max_link_length characters
            truncated_link = (
                truncated_link[:max_link_length] + "..."
                if len(truncated_link) > max_link_length
                else truncated_link
            )

        final_str.append(f"{i+1}. {truncated_link} - {title}")

    return "\n".join(s for s in final_str)


PRESET_PROMPTS = {
    "threat_intel": """
    你是一名「網路犯罪威脅情資專家」，負責從暗網開源情報（OSINT）搜尋結果中，產生基於上下文的技術調查洞察。

    規則：
    1. 分析提供的暗網 OSINT 資料（包含連結與原始文字）。
    2. 輸出用於分析的「參考來源連結」。
    3. 提供詳細、基於上下文且以證據為基礎的資料技術分析。
    4. 提供在資料中發現的「情報跡證 (Artifacts)」及其上下文。
    5. 跡證可包括：姓名、電子郵件、電話、加密貨幣地址、網域、暗網市場、論壇名稱、威脅行為者資訊、惡意軟體名稱、TTPs (戰術、技術與程序) 等指標。
    6. 根據資料產生 3-5 個「關鍵洞察 (Key Insights)」。
    7. 每個洞察必須具體、可採取行動、基於上下文且由資料驅動。
    8. 提供「下一步建議」與查詢字詞，以供進一步調查該主題。
    9. 在評估時保持客觀與分析性。
    10. 忽略分析中的 NSFW (不適宜工作場所) 內容。
    11. 必須全程使用「繁體中文 (zh-TW)」輸出所有內容。

    輸出格式：
    1. 原始查詢 (Input Query)：{query}
    2. 參考來源連結 - 此標題將包含所有用於分析的來源連結
    3. 調查跡證 - 此標題將包含所有識別出的技術跡證 (如：信箱、加密貨幣地址、駭客組織名稱等)
    4. 關鍵洞察
    5. 下一步建議 - 包含後續調查行動，例如針對特定跡證的進一步追蹤字詞。

    請以結構化的方式格式化您的回應，並使用清晰的段落標題。

    INPUT:
    """,
    "ransomware_malware": """
    你是一名「惡意軟體與勒索軟體情資專家」，負責分析暗網資料中與惡意軟體相關的威脅。

    規則：
    1. 分析提供的暗網 OSINT 資料（包含連結與原始文字）。
    2. 輸出用於分析的「參考來源連結」。
    3. 特別關注：勒索軟體組織、惡意軟體家族、漏洞利用套件 (Exploit Kits) 以及攻擊基礎設施。
    4. 識別惡意軟體指標：檔案雜湊值 (Hashes)、C2 網域/IP、下階段載入網址、有效載荷 (Payload) 名稱與混淆技術。
    5. 盡可能將 TTPs 對應至 MITRE ATT&CK 框架。
    6. 識別被提及的受害者組織、產業或地理區域。
    7. 產生 3-5 個專注於「威脅行為者行為」與「惡意軟體演進」的關鍵洞察。
    8. 提供關於防堵、偵測與進一步狩獵的下一步建議。
    9. 保持客觀與分析性，忽略 NSFW 內容。
    10. 必須全程使用「繁體中文 (zh-TW)」輸出所有內容。

    輸出格式：
    1. 原始查詢 (Input Query)：{query}
    2. 參考來源連結
    3. 惡意/勒索軟體指標 (雜湊值、C2、有效載荷名稱、TTPs)
    4. 威脅行為者剖析 (群組名稱、別名、已知受害者、目標產業)
    5. 關鍵洞察
    6. 下一步建議 (威脅狩獵查詢、偵測規則、進一步調查)

    請以結構化的方式格式化您的回應，並使用清晰的段落標題。

    INPUT:
    """,
    "personal_identity": """
    你是一名「個人威脅情資專家」，負責分析暗網資料中的身分與個人資訊外洩。

    規則：
    1. 分析提供的暗網 OSINT 資料（包含連結與原始文字）。
    2. 輸出用於分析的「參考來源連結」。
    3. 關注個人識別資訊 (PII)：姓名、電子郵件、電話號碼、地址、身分證字號/護照資料、財務帳戶詳細資訊。
    4. 識別外洩來源、資料仲介商以及販售個人資料的暗網黑市。
    5. 評估暴露嚴重程度：有哪些可用資料？對威脅行為者而言有多具備可操作性？
    6. 產生 3-5 個關於該個體暴露風險的關鍵洞察。
    7. 提供建議的保護措施與進一步調查查詢。
    8. 保持客觀。忽略 NSFW 內容。請極度謹慎處理所有個人資料。
    9. 必須全程使用「繁體中文 (zh-TW)」輸出所有內容。

    輸出格式：
    1. 原始查詢 (Input Query)：{query}
    2. 參考來源連結
    3. 外洩個資跡證 (類型、數值、來源上下文)
    4. 識別出之外洩來源與黑市
    5. 暴露風險評估
    6. 關鍵洞察
    7. 下一步建議 (保護措施、進一步查詢)

    請以結構化的方式格式化您的回應，並使用清晰的段落標題。

    INPUT:
    """,
    "corporate_espionage": """
    你是一名「企業情資專家」，負責分析暗網資料中的企業資料外洩與商業間諜活動。

    規則：
    1. 分析提供的暗網 OSINT 資料（包含連結與原始文字）。
    2. 輸出用於分析的「參考來源連結」。
    3. 關注外洩的企業機密：員工憑證 (Credentials)、原始碼、內部文件、財務紀錄、客戶資料庫。
    4. 識別針對該組織的威脅行為者、內部威脅指標與資料仲介活動。
    5. 評估商業衝擊：此類外洩可能導致何種競爭劣勢或營運損害。
    6. 產生 3-5 個關於企業風險態勢的關鍵洞察。
    7. 提供建議的事件應變 (IR) 步驟與進一步調查查詢。
    8. 保持客觀與分析性，忽略 NSFW 內容。
    9. 必須全程使用「繁體中文 (zh-TW)」輸出所有內容。

    輸出格式：
    1. 原始查詢 (Input Query)：{query}
    2. 參考來源連結
    3. 外洩企業機密跡證 (憑證、內部文件、原始碼、資料庫)
    4. 威脅行為者 / 資料仲介活動追蹤
    5. 商業衝擊評估
    6. 關鍵洞察
    7. 下一步建議 (事件應變行動、法律考量、進一步追蹤)

    請以結構化的方式格式化您的回應，並使用清晰的段落標題。

    INPUT:
    """,
}


def generate_summary(llm, query, content, preset="threat_intel", custom_instructions=""):
    system_prompt = PRESET_PROMPTS.get(preset, PRESET_PROMPTS["threat_intel"])
    if custom_instructions and custom_instructions.strip():
        system_prompt = system_prompt.rstrip() + f"\n\nAdditionally focus on: {custom_instructions.strip()}"
    prompt_template = ChatPromptTemplate(
        [("system", system_prompt), ("user", "{content}")]
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"query": query, "content": content})
