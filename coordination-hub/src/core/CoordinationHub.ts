import express from "express";
import { EventEmitter } from "events";
import { AgentManager } from "./AgentManager";
import { TaskScheduler } from "./TaskScheduler";
import { CommunicationEngine } from "./CommunicationEngine";
import { QualityGateManager } from "./QualityGateManager";
import { ConflictResolver } from "./ConflictResolver";
import { DatabaseManager } from "./DatabaseManager";
import { Logger } from "../utils/Logger";
export class CoordinationHub extends EventEmitter {
  private agentManager: AgentManager;
  private taskScheduler: TaskScheduler;
  private communicationEngine: CommunicationEngine;
  private qualityGateManager: QualityGateManager;
  private conflictResolver: ConflictResolver;
  private databaseManager: DatabaseManager;
  private logger: Logger;
  private router: express.Router;
  constructor() {
    super();
    this.agentManager = new AgentManager();
    this.taskScheduler = new TaskScheduler();
    this.communicationEngine = new CommunicationEngine();
    this.qualityGateManager = new QualityGateManager();
    this.conflictResolver = new ConflictResolver();
    this.databaseManager = new DatabaseManager();
    this.logger = new Logger();
    this.router = express.Router();
  }
  async initialize() {
    this.logger.info("🔧 Initializing Coordination Hub...");
    await this.databaseManager.initialize();
    await this.agentManager.initialize();
    await this.taskScheduler.initialize();
    await this.communicationEngine.initialize();
    await this.qualityGateManager.initialize();
    await this.conflictResolver.initialize();
    this.setupRoutes();
    this.logger.info("✅ Coordination Hub initialized");
  }
  private setupRoutes() {
    this.router.post("/auth/login", async (req, res) => {
      try {
        const { agentId, password } = req.body;
        const result = await this.agentManager.authenticate(agentId, password);
        if (result.success) {
          res.json({ success: true, token: result.token, agent: result.agent });
        } else {
          res.status(401).json({ success: false, error: result.error });
        }
      } catch (error) {
        this.logger.error("Login error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.get("/agents/:agentId/status", async (req, res) => {
      try {
        const { agentId } = req.params;
        const agent = await this.agentManager.getAgent(agentId);
        if (agent) {
          res.json({ success: true, agent });
        } else {
          res.status(404).json({ success: false, error: "Agent not found" });
        }
      } catch (error) {
        this.logger.error("Get agent status error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.post("/agents/:agentId/progress", async (req, res) => {
      try {
        const { agentId } = req.params;
        const progressData = req.body;
        const result = await this.agentManager.updateProgress(
          agentId,
          progressData,
        );
        if (result.success) {
          this.emit("progressUpdate", { agentId, progress: progressData });
          res.json({ success: true, message: "Progress updated successfully" });
        } else {
          res.status(400).json({ success: false, error: result.error });
        }
      } catch (error) {
        this.logger.error("Update progress error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.post("/messages", async (req, res) => {
      try {
        const { to, message, priority = "medium", from } = req.body;
        const result = await this.communicationEngine.sendMessage(
          to,
          message,
          priority,
          from,
        );
        if (result.success) {
          res.json({ success: true, messageId: result.messageId });
        } else {
          res.status(400).json({ success: false, error: result.error });
        }
      } catch (error) {
        this.logger.error("Send message error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.get("/agents/:agentId/messages", async (req, res) => {
      try {
        const { agentId } = req.params;
        const messages =
          await this.communicationEngine.getMessagesForAgent(agentId);
        res.json({ success: true, messages });
      } catch (error) {
        this.logger.error("Get messages error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.get("/agents", async (req, res) => {
      try {
        const agents = await this.agentManager.getAllAgents();
        res.json({ success: true, agents });
      } catch (error) {
        this.logger.error("Get agents error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.get("/status", async (req, res) => {
      try {
        const status = {
          agents: await this.agentManager.getAllAgents(),
          tasks: await this.taskScheduler.getAllTasks(),
          conflicts: await this.conflictResolver.getAllConflicts(),
          qualityGates: await this.qualityGateManager.getAllQualityGates(),
          timestamp: new Date().toISOString(),
        };
        res.json({ success: true, status });
      } catch (error) {
        this.logger.error("Get status error", error);
        res
          .status(500)
          .json({ success: false, error: "Internal server error" });
      }
    });
    this.router.get("/health", (req, res) => {
      res.json({
        status: "healthy",
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
      });
    });
  }
  getRouter(): express.Router {
    return this.router;
  }
  async authenticateSocket(socket: any, data: any) {
    try {
      const { agentId, token } = data;
      const result = await this.agentManager.verifyToken(agentId, token);
      if (result.success) {
        socket.agentId = agentId;
        socket.join(`agent_${agentId}`);
        this.logger.info("Socket authenticated", {
          agentId,
          socketId: socket.id,
        });
        socket.emit("auth_success", { agentId });
      } else {
        socket.emit("auth_error", { error: result.error });
      }
    } catch (error) {
      this.logger.error("Socket authentication error", error);
      socket.emit("auth_error", { error: "Authentication failed" });
    }
  }
}
