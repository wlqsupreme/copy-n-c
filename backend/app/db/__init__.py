"""
数据库模块
提供Supabase数据库连接和操作功能
"""

from .client import db_client, init_database, close_database
from .models import (
    User, Project, SourceText, Character, Storyboard, StoryboardPage, StoryboardPanel,
    ProjectVisibility, TableNames, UserFields, ProjectFields, SourceTextFields, CharacterFields
)
from .crud import (
    # 用户操作
    create_user, get_user_by_id, get_user_by_username, get_user_by_email, update_user_credit,
    # 项目操作
    create_project, get_project_by_id, get_projects_by_user, update_project, delete_project,
    # 原文操作
    create_source_text, get_source_texts_by_project, save_storyboard, load_storyboard,
    # 角色操作
    create_character, get_characters_by_project, update_character, delete_character,
    # 公共查询
    get_public_projects, search_projects, get_user_stats
)

__all__ = [
    # 客户端
    'db_client', 'init_database', 'close_database',
    # 模型
    'User', 'Project', 'SourceText', 'Character', 'Storyboard', 'StoryboardPage', 'StoryboardPanel',
    'ProjectVisibility', 'TableNames', 'UserFields', 'ProjectFields', 'SourceTextFields', 'CharacterFields',
    # CRUD操作
    'create_user', 'get_user_by_id', 'get_user_by_username', 'get_user_by_email', 'update_user_credit',
    'create_project', 'get_project_by_id', 'get_projects_by_user', 'update_project', 'delete_project',
    'create_source_text', 'get_source_texts_by_project', 'save_storyboard', 'load_storyboard',
    'create_character', 'get_characters_by_project', 'update_character', 'delete_character',
    'get_public_projects', 'search_projects', 'get_user_stats'
]
