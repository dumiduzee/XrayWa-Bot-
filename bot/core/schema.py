from pydantic import BaseModel
from typing import Optional


class DeviceListMetadata(BaseModel):
    senderKeyHash: Optional[str] = None
    senderTimestamp: Optional[str] = None
    recipientKeyHash: Optional[str] = None
    recipientTimestamp: Optional[str] = None


class MessageContextInfo(BaseModel):
    deviceListMetadata: Optional[DeviceListMetadata] = None
    deviceListMetadataVersion: Optional[int] = None
    messageSecret: Optional[str] = None


class ExtendedTextMessage(BaseModel):
    text: str
    previewType: Optional[str] = None
    inviteLinkGroupTypeV2: Optional[str] = None


class MessageContent(BaseModel):
    conversation: Optional[str] = None
    extendedTextMessage: Optional[ExtendedTextMessage] = None
    messageContextInfo: Optional[MessageContextInfo] = None


class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str
    senderLid: Optional[str] = None  # sometimes missing


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
