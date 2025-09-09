from typing import Any, Tuple

from podcast.formats.article import ArticleInfo
from podcast.helpers.prompt import PromptHelper
from podcast.helpers.response import ResponseHelper
from podcast.services.openai_auth import OpenAIAuthService
from podcast.services.openai_text_gen import OpenAITextGenService
from podcast.utilities.bundle import UtilitiesBundle


class TextGenerationManager:
    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.path = path
        self.client: Any = OpenAIAuthService(utilities=self.utilities).client
        self.text_gen_service: OpenAITextGenService = OpenAITextGenService(client=self.client, utilities=self.utilities)
        self.prompt_helper: PromptHelper = PromptHelper(path=self.path, utilities=self.utilities)
        self.response_helper: ResponseHelper = ResponseHelper(utilities=self.utilities)

    def generate_script(self, article: ArticleInfo, persona: str) -> str:
        system_prompt, user_prompt = self.prompt_helper.assemble_script_prompts(article=article, persona=persona)
        script: str = self.text_gen_service.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        cleaned_script = self.response_helper.remove_special_characters(text=script)
        return cleaned_script

    def generate_description(self, script: str) -> str:
        system_prompt, user_prompt = self.prompt_helper.assemble_description_prompts(script=script)
        description: str = self.text_gen_service.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        return description

    def generate_title(self, script: str) -> str:
        system_prompt, user_prompt = self.prompt_helper.assemble_title_prompts(script=script)
        title: str = self.text_gen_service.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        cleaned_title = self.response_helper.remove_quotes_from_title(title=title)
        return cleaned_title

    def generate_social_media_post(self, script: str) -> str:
        system_prompt, user_prompt = self.prompt_helper.assemble_social_media_prompts(script=script)
        post: str = self.text_gen_service.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        return post

    def generate_score(self, article: ArticleInfo) -> Tuple[int, str]:
        """
        Generates a score for an article based on the given prompt using the text generation service.
        """
        system_prompt, user_prompt = self.prompt_helper.assemble_scoring_prompts(article=article)
        response: str = self.text_gen_service.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        score, justification = self.response_helper.parse_score_and_justification(response=response)
        return score, justification
