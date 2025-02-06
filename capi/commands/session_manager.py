from typing import Optional
from dataclasses import dataclass
from .designer_mode.xml_manager import XMLManager

@dataclass
class DesignerModeContext:
    xml_manager: XMLManager
    current_path: list
    is_active: bool = False

class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._designer_context = DesignerModeContext(
                xml_manager=None,
                current_path=[],
                is_active=False
            )
        return cls._instance
    
    @property
    def designer_context(self) -> DesignerModeContext:
        return self._designer_context
    
    def start_designer_session(self, xml_manager: XMLManager, current_path: list) -> None:
        self._designer_context.xml_manager = xml_manager
        self._designer_context.current_path = current_path
        self._designer_context.is_active = True
    
    def end_designer_session(self) -> None:
        self._designer_context.is_active = False
        self._designer_context.xml_manager = None
        self._designer_context.current_path = []
    
    def is_designer_session_active(self) -> bool:
        return self._designer_context.is_active