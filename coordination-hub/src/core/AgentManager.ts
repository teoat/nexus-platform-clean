import { EventEmitter } from "events";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import { DatabaseManager } from "./DatabaseManager";
import { Logger } from "../utils/Logger";
export interface Agent {
  id: string;
  name: string;
  role: string;
  status: "active" | "blocked" | "completed" | "offline";
  currentTask?: string;
  progress: number;
  lastUpdate: Date;
  capabilities: string[];
  dependencies: string[];
  blockers: string[];
}
export class AgentManager extends EventEmitter {
  private agents: Map<string, Agent> = new Map();
  private agentCredentials: Map<string, string> = new Map();
  private databaseManager: DatabaseManager;
  private logger: Logger;
  constructor() {
    super();
    this.databaseManager = new DatabaseManager();
    this.logger = new Logger();
  }
  async initialize() {
    this.logger.info("🔧 Initializing Agent Manager...");
    await this.databaseManager.initialize();
    await this.initializeAgents();
    this.logger.info("✅ Agent Manager initialized");
  }
  private async initializeAgents() {
    const agentConfigs = [
      {
        id: "agent1",
        name: "Security & Infrastructure Specialist",
        role: "Security Expert, DevOps Engineer, Infrastructure Manager",
        capabilities: [
          "security",
          "infrastructure",
          "devops",
          "monitoring",
          "compliance",
        ],
      },
      {
        id: "agent2",
        name: "Frontend Consolidation Expert",
        role: "Frontend Developer, UI/UX Specialist, Component Architect",
        capabilities: [
          "frontend",
          "react",
          "typescript",
          "ui",
          "ux",
          "consolidation",
        ],
      },
      {
        id: "agent3",
        name: "Backend Consolidation Expert",
        role: "Backend Developer, API Architect, Microservices Specialist",
        capabilities: [
          "backend",
          "fastapi",
          "python",
          "apis",
          "microservices",
          "consolidation",
        ],
      },
      {
        id: "agent4",
        name: "Database & API Integration Specialist",
        role: "Database Administrator, Integration Specialist, Data Architect",
        capabilities: [
          "database",
          "postgresql",
          "redis",
          "integration",
          "migration",
          "optimization",
        ],
      },
      {
        id: "agent5",
        name: "Testing & Quality Assurance Expert",
        role: "QA Engineer, Test Automation Specialist, Quality Manager",
        capabilities: [
          "testing",
          "quality",
          "automation",
          "ci-cd",
          "validation",
          "documentation",
        ],
      },
    ];
    for (const config of agentConfigs) {
      const agent: Agent = {
        ...config,
        status: "offline",
        progress: 0,
        lastUpdate: new Date(),
        dependencies: [],
        blockers: [],
      };
      this.agents.set(agent.id, agent);
      const password =
        process.env[`${agent.id.toUpperCase()}_PASSWORD`] ||
        `${agent.id}-password-2024`;
      this.agentCredentials.set(agent.id, password);
    }
  }
  async authenticate(agentId: string, password: string) {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) {
        return { success: false, error: "Agent not found" };
      }
      const storedPassword = this.agentCredentials.get(agentId);
      if (!storedPassword || password !== storedPassword) {
        return { success: false, error: "Invalid credentials" };
      }
      const token = jwt.sign(
        { agentId, role: agent.role },
        process.env.JWT_SECRET || "default-secret",
        { expiresIn: "24h" },
      );
      agent.status = "active";
      agent.lastUpdate = new Date();
      this.emit("agentStatusChanged", agentId, "active");
      return {
        success: true,
        token,
        agent: {
          id: agent.id,
          name: agent.name,
          role: agent.role,
          status: agent.status,
          progress: agent.progress,
        },
      };
    } catch (error) {
      this.logger.error("Authentication error", error);
      return { success: false, error: "Authentication failed" };
    }
  }
  async verifyToken(agentId: string, token: string) {
    try {
      const decoded = jwt.verify(
        token,
        process.env.JWT_SECRET || "default-secret",
      ) as any;
      if (decoded.agentId !== agentId) {
        return { success: false, error: "Invalid token" };
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: "Invalid token" };
    }
  }
  async updateProgress(agentId: string, progressData: any) {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) {
        return { success: false, error: "Agent not found" };
      }
      if (progressData.progress) {
        agent.progress = progressData.progress.overall || agent.progress;
      }
      if (progressData.status) {
        agent.status = progressData.status;
      }
      agent.lastUpdate = new Date();
      await this.databaseManager.storeProgress(agentId, progressData);
      this.emit("agentProgressUpdated", agentId, progressData);
      return { success: true };
    } catch (error) {
      this.logger.error("Update progress error", error);
      return { success: false, error: "Failed to update progress" };
    }
  }
  async getAgent(agentId: string): Promise<Agent | undefined> {
    return this.agents.get(agentId);
  }
  async getAllAgents(): Promise<Agent[]> {
    return Array.from(this.agents.values());
  }
  async updateAgentStatus(
    agentId: string,
    status: Agent["status"],
    progress?: number,
  ) {
    const agent = this.agents.get(agentId);
    if (!agent) throw new Error(`Agent ${agentId} not found`);
    agent.status = status;
    agent.lastUpdate = new Date();
    if (progress !== undefined) agent.progress = progress;
    this.emit("agentStatusChanged", agentId, status);
    return agent;
  }
}
