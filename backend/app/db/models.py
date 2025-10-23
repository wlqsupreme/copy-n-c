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
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SourceTextFields:
    """原文表字段"""
    TEXT_ID = "text_id"
    PROJECT_ID = "project_id"
    TITLE = "title"
    RAW_CONTENT = "raw_content"
    ORDER_INDEX = "order_index"
    CREATED_AT = "created_at"


class CharacterFields:
    """角色表字段"""
    CHARACTER_ID = "character_id"
    PROJECT_ID = "project_id"
    NAME = "name"
    DESCRIPTION = "description"
    REFERENCE_IMAGE_URLS = "reference_image_urls"
    LORA_MODEL_PATH = "lora_model_path"
    TRIGGER_WORD = "trigger_word"


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
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.project_id = project_id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.visibility = visibility
        self.default_style_prompt = default_style_prompt
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
        created_at: Optional[datetime] = None
    ):
        self.text_id = text_id or str(uuid.uuid4())
        self.project_id = project_id
        self.title = title
        self.raw_content = raw_content
        self.order_index = order_index
        self.created_at = created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            SourceTextFields.TEXT_ID: self.text_id,
            SourceTextFields.PROJECT_ID: self.project_id,
            SourceTextFields.TITLE: self.title,
            SourceTextFields.RAW_CONTENT: self.raw_content,
            SourceTextFields.ORDER_INDEX: self.order_index,
            SourceTextFields.CREATED_AT: self.created_at
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
            created_at=data.get(SourceTextFields.CREATED_AT)
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
    """分镜面板模型"""
    
    def __init__(
        self,
        panel_index: int = 1,
        description: str = "",
        characters: Optional[List[str]] = None,
        dialogue: Optional[List[str]] = None,
        camera_angle: Optional[str] = None,
        emotion: Optional[str] = None
    ):
        self.panel_index = panel_index
        self.description = description
        self.characters = characters or []
        self.dialogue = dialogue or []
        self.camera_angle = camera_angle
        self.emotion = emotion
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "panel_index": self.panel_index,
            "description": self.description,
            "characters": self.characters,
            "dialogue": self.dialogue,
            "camera_angle": self.camera_angle,
            "emotion": self.emotion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryboardPanel':
        """从字典创建实例"""
        return cls(
            panel_index=data.get("panel_index", 1),
            description=data.get("description", ""),
            characters=data.get("characters", []),
            dialogue=data.get("dialogue", []),
            camera_angle=data.get("camera_angle"),
            emotion=data.get("emotion")
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
