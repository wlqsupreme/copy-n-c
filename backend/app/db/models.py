"""
数据模型定义
定义数据库表结构和字段常量
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ProjectVisibility(str, Enum):
    """项目可见性枚举"""
    PRIVATE = "private"
    PUBLIC = "public"


# 表名常量
class TableNames:
    """数据库表名常量"""
    USERS = "users"
    PROJECTS = "projects"
    SOURCE_TEXTS = "source_texts"
    CHARACTERS = "characters"
    STORYBOARDS = "storyboards"


# 字段名常量
class UserFields:
    """用户表字段"""
    USER_ID = "user_id"
    USERNAME = "username"
    EMAIL = "email"
    HASHED_PASSWORD = "hashed_password"
    CREDIT_BALANCE = "credit_balance"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ProjectFields:
    """项目表字段"""
    PROJECT_ID = "project_id"
    USER_ID = "user_id"
    TITLE = "title"
    DESCRIPTION = "description"
    VISIBILITY = "visibility"
    DEFAULT_STYLE_PROMPT = "default_style_prompt"
    UPLOAD_METHOD = "upload_method"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SourceTextFields:
    """原文表字段"""
    TEXT_ID = "text_id"
    PROJECT_ID = "project_id"
    TITLE = "title"
    RAW_CONTENT = "raw_content"
    ORDER_INDEX = "order_index"
    CHAPTER_NUMBER = "chapter_number"
    CHAPTER_NAME = "chapter_name"
    CREATED_AT = "created_at"
    PROCESSING_STATUS = "processing_status"
    ERROR_MESSAGE = "error_message"


class CharacterFields:
    """角色表字段"""
    CHARACTER_ID = "character_id"
    PROJECT_ID = "project_id"
    NAME = "name"
    DESCRIPTION = "description"
    REFERENCE_IMAGE_URLS = "reference_image_urls"
    LORA_MODEL_PATH = "lora_model_path"
    TRIGGER_WORD = "trigger_word"


class StoryboardFields:
    """分镜表字段"""
    STORYBOARD_ID = "storyboard_id"
    PROJECT_ID = "project_id"
    SOURCE_TEXT_ID = "source_text_id"
    PANEL_INDEX = "panel_index"
    ORIGINAL_TEXT_SNIPPET = "original_text_snippet"
    CHARACTER_APPEARANCE = "character_appearance"
    SCENE_AND_LIGHTING = "scene_and_lighting"
    CAMERA_AND_COMPOSITION = "camera_and_composition"
    EXPRESSION_AND_ACTION = "expression_and_action"
    STYLE_REQUIREMENTS = "style_requirements"
    GENERATED_IMAGE_URL = "generated_image_url"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CHARACTER_ID = "character_id"


# 数据模型类
class User:
    """用户模型"""
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        username: str = "",
        email: str = "",
        hashed_password: str = "",
        credit_balance: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.credit_balance = credit_balance
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            UserFields.USER_ID: self.user_id,
            UserFields.USERNAME: self.username,
            UserFields.EMAIL: self.email,
            UserFields.HASHED_PASSWORD: self.hashed_password,
            UserFields.CREDIT_BALANCE: self.credit_balance,
            UserFields.CREATED_AT: self.created_at,
            UserFields.UPDATED_AT: self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建实例"""
        return cls(
            user_id=data.get(UserFields.USER_ID),
            username=data.get(UserFields.USERNAME, ""),
            email=data.get(UserFields.EMAIL, ""),
            hashed_password=data.get(UserFields.HASHED_PASSWORD, ""),
            credit_balance=data.get(UserFields.CREDIT_BALANCE, 0),
            created_at=data.get(UserFields.CREATED_AT),
            updated_at=data.get(UserFields.UPDATED_AT)
        )


class Project:
    """项目模型"""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        user_id: str = "",
        title: str = "",
        description: Optional[str] = None,
        visibility: ProjectVisibility = ProjectVisibility.PRIVATE,
        default_style_prompt: Optional[str] = None,
        upload_method: str = "single_chapter",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.project_id = project_id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.visibility = visibility
        self.default_style_prompt = default_style_prompt
        self.upload_method = upload_method
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            ProjectFields.PROJECT_ID: self.project_id,
            ProjectFields.USER_ID: self.user_id,
            ProjectFields.TITLE: self.title,
            ProjectFields.DESCRIPTION: self.description,
            ProjectFields.VISIBILITY: self.visibility.value,
            ProjectFields.DEFAULT_STYLE_PROMPT: self.default_style_prompt,
            ProjectFields.UPLOAD_METHOD: self.upload_method,
            ProjectFields.CREATED_AT: self.created_at,
            ProjectFields.UPDATED_AT: self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """从字典创建实例"""
        return cls(
            project_id=data.get(ProjectFields.PROJECT_ID),
            user_id=data.get(ProjectFields.USER_ID, ""),
            title=data.get(ProjectFields.TITLE, ""),
            description=data.get(ProjectFields.DESCRIPTION),
            visibility=ProjectVisibility(data.get(ProjectFields.VISIBILITY, ProjectVisibility.PRIVATE.value)),
            default_style_prompt=data.get(ProjectFields.DEFAULT_STYLE_PROMPT),
            upload_method=data.get(ProjectFields.UPLOAD_METHOD, "single_chapter"),
            created_at=data.get(ProjectFields.CREATED_AT),
            updated_at=data.get(ProjectFields.UPDATED_AT)
        )


class SourceText:
    """原文模型"""
    
    def __init__(
        self,
        text_id: Optional[str] = None,
        project_id: str = "",
        title: str = "Untitled Chapter",
        raw_content: str = "",
        order_index: int = 0,
        chapter_number: Optional[int] = None,
        chapter_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        processing_status: str = "pending",
        error_message: Optional[str] = None
    ):
        self.text_id = text_id or str(uuid.uuid4())
        self.project_id = project_id
        self.title = title
        self.raw_content = raw_content
        self.order_index = order_index
        self.chapter_number = chapter_number
        self.chapter_name = chapter_name
        self.created_at = created_at
        self.processing_status = processing_status
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            SourceTextFields.TEXT_ID: self.text_id,
            SourceTextFields.PROJECT_ID: self.project_id,
            SourceTextFields.TITLE: self.title,
            SourceTextFields.RAW_CONTENT: self.raw_content,
            SourceTextFields.ORDER_INDEX: self.order_index,
            SourceTextFields.CHAPTER_NUMBER: self.chapter_number,
            SourceTextFields.CHAPTER_NAME: self.chapter_name,
            SourceTextFields.CREATED_AT: self.created_at,
            SourceTextFields.PROCESSING_STATUS: self.processing_status,
            SourceTextFields.ERROR_MESSAGE: self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SourceText':
        """从字典创建实例"""
        return cls(
            text_id=data.get(SourceTextFields.TEXT_ID),
            project_id=data.get(SourceTextFields.PROJECT_ID, ""),
            title=data.get(SourceTextFields.TITLE, "Untitled Chapter"),
            raw_content=data.get(SourceTextFields.RAW_CONTENT, ""),
            order_index=data.get(SourceTextFields.ORDER_INDEX, 0),
            chapter_number=data.get(SourceTextFields.CHAPTER_NUMBER),
            chapter_name=data.get(SourceTextFields.CHAPTER_NAME),
            created_at=data.get(SourceTextFields.CREATED_AT),
            processing_status=data.get(SourceTextFields.PROCESSING_STATUS, "pending"),
            error_message=data.get(SourceTextFields.ERROR_MESSAGE)
        )


class Character:
    """角色模型"""
    
    def __init__(
        self,
        character_id: Optional[str] = None,
        project_id: str = "",
        name: str = "",
        description: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        lora_model_path: Optional[str] = None,
        trigger_word: Optional[str] = None
    ):
        self.character_id = character_id or str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.description = description
        self.reference_image_urls = reference_image_urls or []
        self.lora_model_path = lora_model_path
        self.trigger_word = trigger_word
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            CharacterFields.CHARACTER_ID: self.character_id,
            CharacterFields.PROJECT_ID: self.project_id,
            CharacterFields.NAME: self.name,
            CharacterFields.DESCRIPTION: self.description,
            CharacterFields.REFERENCE_IMAGE_URLS: self.reference_image_urls,
            CharacterFields.LORA_MODEL_PATH: self.lora_model_path,
            CharacterFields.TRIGGER_WORD: self.trigger_word
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """从字典创建实例"""
        return cls(
            character_id=data.get(CharacterFields.CHARACTER_ID),
            project_id=data.get(CharacterFields.PROJECT_ID, ""),
            name=data.get(CharacterFields.NAME, ""),
            description=data.get(CharacterFields.DESCRIPTION),
            reference_image_urls=data.get(CharacterFields.REFERENCE_IMAGE_URLS, []),
            lora_model_path=data.get(CharacterFields.LORA_MODEL_PATH),
            trigger_word=data.get(CharacterFields.TRIGGER_WORD)
        )


# 分镜相关模型
class StoryboardPanel:
    """分镜面板模型（数据库表结构）"""
    
    def __init__(
        self,
        storyboard_id: Optional[str] = None,
        project_id: str = "",
        source_text_id: str = "",
        panel_index: int = 0,
        original_text_snippet: Optional[str] = None,
        character_appearance: Optional[str] = None,
        scene_and_lighting: Optional[str] = None,
        camera_and_composition: Optional[str] = None,
        expression_and_action: Optional[str] = None,
        style_requirements: Optional[str] = None,
        generated_image_url: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        character_id: Optional[str] = None
    ):
        self.storyboard_id = storyboard_id or str(uuid.uuid4())
        self.project_id = project_id
        self.source_text_id = source_text_id
        self.panel_index = panel_index
        self.original_text_snippet = original_text_snippet
        self.character_appearance = character_appearance
        self.scene_and_lighting = scene_and_lighting
        self.camera_and_composition = camera_and_composition
        self.expression_and_action = expression_and_action
        self.style_requirements = style_requirements
        self.generated_image_url = generated_image_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.character_id = character_id
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            StoryboardFields.STORYBOARD_ID: self.storyboard_id,
            StoryboardFields.PROJECT_ID: self.project_id,
            StoryboardFields.SOURCE_TEXT_ID: self.source_text_id,
            StoryboardFields.PANEL_INDEX: self.panel_index,
            StoryboardFields.ORIGINAL_TEXT_SNIPPET: self.original_text_snippet,
            StoryboardFields.CHARACTER_APPEARANCE: self.character_appearance,
            StoryboardFields.SCENE_AND_LIGHTING: self.scene_and_lighting,
            StoryboardFields.CAMERA_AND_COMPOSITION: self.camera_and_composition,
            StoryboardFields.EXPRESSION_AND_ACTION: self.expression_and_action,
            StoryboardFields.STYLE_REQUIREMENTS: self.style_requirements,
            StoryboardFields.GENERATED_IMAGE_URL: self.generated_image_url,
            StoryboardFields.CREATED_AT: self.created_at,
            StoryboardFields.UPDATED_AT: self.updated_at,
            StoryboardFields.CHARACTER_ID: self.character_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryboardPanel':
        """从字典创建实例"""
        return cls(
            storyboard_id=data.get(StoryboardFields.STORYBOARD_ID),
            project_id=data.get(StoryboardFields.PROJECT_ID, ""),
            source_text_id=data.get(StoryboardFields.SOURCE_TEXT_ID, ""),
            panel_index=data.get(StoryboardFields.PANEL_INDEX, 0),
            original_text_snippet=data.get(StoryboardFields.ORIGINAL_TEXT_SNIPPET),
            character_appearance=data.get(StoryboardFields.CHARACTER_APPEARANCE),
            scene_and_lighting=data.get(StoryboardFields.SCENE_AND_LIGHTING),
            camera_and_composition=data.get(StoryboardFields.CAMERA_AND_COMPOSITION),
            expression_and_action=data.get(StoryboardFields.EXPRESSION_AND_ACTION),
            style_requirements=data.get(StoryboardFields.STYLE_REQUIREMENTS),
            generated_image_url=data.get(StoryboardFields.GENERATED_IMAGE_URL),
            created_at=data.get(StoryboardFields.CREATED_AT),
            updated_at=data.get(StoryboardFields.UPDATED_AT),
            character_id=data.get(StoryboardFields.CHARACTER_ID)
        )


class StoryboardPage:
    """分镜页面模型"""
    
    def __init__(
        self,
        page_index: int = 1,
        panels: Optional[List[StoryboardPanel]] = None
    ):
        self.page_index = page_index
        self.panels = panels or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "page_index": self.page_index,
            "panels": [panel.to_dict() for panel in self.panels]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryboardPage':
        """从字典创建实例"""
        panels_data = data.get("panels", [])
        panels = [StoryboardPanel.from_dict(panel_data) for panel_data in panels_data]
        return cls(
            page_index=data.get("page_index", 1),
            panels=panels
        )


class Storyboard:
    """分镜模型"""
    
    def __init__(
        self,
        pages: Optional[List[StoryboardPage]] = None
    ):
        self.pages = pages or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "pages": [page.to_dict() for page in self.pages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Storyboard':
        """从字典创建实例"""
        pages_data = data.get("pages", [])
        pages = [StoryboardPage.from_dict(page_data) for page_data in pages_data]
        return cls(pages=pages)
