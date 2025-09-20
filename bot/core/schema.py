from pydantic import BaseModel
from typing import Optional

class DeviceListMetadata(BaseModel):
    senderKeyHash: Optional[str] = None
    senderTimestamp: str
    recipientKeyHash: str
    recipientTimestamp: str

class MessageContextInfo(BaseModel):
    deviceListMetadata: DeviceListMetadata
    deviceListMetadataVersion: int
    messageSecret: str

class MessageContent(BaseModel):
    conversation: str
    messageContextInfo: MessageContextInfo

class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str
    senderLid: Optional[str]  # optional in case it’s missing sometimes

class Messages(BaseModel):
    key: MessageKey
    messageTimestamp: int
    pushName: str
    broadcast: bool
    message: MessageContent
    remoteJid: str
    id: str

class Data(BaseModel):
    messages: Messages

class WhatsAppEvent(BaseModel):
    event: str
    sessionId: str
    data: Data
    timestamp: int
