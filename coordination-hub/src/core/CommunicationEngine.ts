import { EventEmitter } from "events";
import { DatabaseManager } from "./DatabaseManager";
import { Logger } from "../utils/Logger";
export interface Message {
  id: string;
  from: string;
  to: string;
  content: string;
  priority: "low" | "medium" | "high" | "critical";
  type: "text" | "task" | "alert" | "notification";
  timestamp: Date;
  read: boolean;
  metadata?: any;
}
export class CommunicationEngine extends EventEmitter {
  private messages: Map<string, Message> = new Map();
  private messageQueues: Map<string, Message[]> = new Map();
  private databaseManager: DatabaseManager;
  private logger: Logger;
  constructor() {
    super();
    this.databaseManager = new DatabaseManager();
    this.logger = new Logger();
  }
  async initialize() {
    this.logger.info("🔧 Initializing Communication Engine...");
    await this.databaseManager.initialize();
    this.setupMessageProcessing();
    this.logger.info("✅ Communication Engine initialized");
  }
  private setupMessageProcessing() {
    setInterval(() => {
      this.processMessageQueues();
    }, 5000);
  }
  private async processMessageQueues() {
    for (const [agentId, queue] of this.messageQueues) {
      if (queue.length > 0) {
        const message = queue.shift();
        if (message) {
          await this.deliverMessage(message);
        }
      }
    }
  }
  async sendMessage(
    to: string,
    content: string,
    priority: Message["priority"] = "medium",
    from: string = "system",
    type: Message["type"] = "text",
    metadata?: any,
  ) {
    try {
      const message: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        from,
        to,
        content,
        priority,
        type,
        timestamp: new Date(),
        read: false,
        metadata,
      };
      if (!this.messageQueues.has(to)) {
        this.messageQueues.set(to, []);
      }
      this.messageQueues.get(to)!.push(message);
      await this.databaseManager.storeMessage(message);
      this.emit("messageSent", message);
      return { success: true, messageId: message.id };
    } catch (error) {
      this.logger.error("Send message error", error);
      return { success: false, error: "Failed to send message" };
    }
  }
  private async deliverMessage(message: Message) {
    try {
      this.logger.info(
        `📨 Delivering message to ${message.to}: ${message.content}`,
      );
      message.read = true;
      this.messages.set(message.id, message);
      this.emit("messageDelivered", message);
    } catch (error) {
      this.logger.error("Deliver message error", error);
    }
  }
  async getMessagesForAgent(agentId: string): Promise<Message[]> {
    try {
      const messages = await this.databaseManager.getMessagesForAgent(agentId);
      return messages || [];
    } catch (error) {
      this.logger.error("Get messages error", error);
      return [];
    }
  }
  async getRecentMessages(limit: number = 50): Promise<Message[]> {
    try {
      const messages = await this.databaseManager.getRecentMessages(limit);
      return messages || [];
    } catch (error) {
      this.logger.error("Get recent messages error", error);
      return [];
    }
  }
  async markMessageAsRead(messageId: string) {
    try {
      const message = this.messages.get(messageId);
      if (message) {
        message.read = true;
        await this.databaseManager.updateMessage(message);
        this.emit("messageRead", messageId);
      }
    } catch (error) {
      this.logger.error("Mark message as read error", error);
    }
  }
}
