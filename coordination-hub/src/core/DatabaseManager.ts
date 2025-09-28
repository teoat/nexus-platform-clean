import sqlite3 from "sqlite3";
import { Logger } from "../utils/Logger";
export class DatabaseManager {
  private db: sqlite3.Database | null = null;
  private logger: Logger;
  constructor() {
    this.logger = new Logger();
  }
  async initialize() {
    this.logger.info("🔧 Initializing Database Manager...");
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database("./data/coordination-hub.db", (err) => {
        if (err) {
          this.logger.error("Database initialization error", err);
          reject(err);
        } else {
          this.logger.info("✅ Database initialized");
          this.createTables().then(resolve).catch(reject);
        }
      });
    });
  }
  private async createTables() {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      const queries = [
        `CREATE TABLE IF NOT EXISTS agents ( id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL, progress INTEGER DEFAULT 0, last_update DATETIME DEFAULT CURRENT_TIMESTAMP, capabilities TEXT, dependencies TEXT, blockers TEXT )`,
        `CREATE TABLE IF NOT EXISTS progress ( id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL, data TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (agent_id) REFERENCES agents (id) )`,
        `CREATE TABLE IF NOT EXISTS messages ( id TEXT PRIMARY KEY, from_agent TEXT NOT NULL, to_agent TEXT NOT NULL, content TEXT NOT NULL, priority TEXT NOT NULL, type TEXT NOT NULL, read_status BOOLEAN DEFAULT FALSE, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, metadata TEXT )`,
        `CREATE TABLE IF NOT EXISTS quality_gates ( id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, criteria TEXT NOT NULL, last_run DATETIME, next_run DATETIME, agent_id TEXT NOT NULL )`,
        `CREATE TABLE IF NOT EXISTS conflicts ( id TEXT PRIMARY KEY, type TEXT NOT NULL, description TEXT NOT NULL, severity TEXT NOT NULL, agents TEXT NOT NULL, status TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, resolved_at DATETIME, resolution TEXT, escalated_to TEXT )`,
      ];
      let completed = 0;
      queries.forEach((query, index) => {
        this.db!.run(query, (err) => {
          if (err) {
            this.logger.error(`Create table ${index} error`, err);
            reject(err);
          } else {
            completed++;
            if (completed === queries.length) {
              this.logger.info("✅ Database tables created");
              resolve();
            }
          }
        });
      });
    });
  }
  async storeProgress(agentId: string, progressData: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "INSERT INTO progress (agent_id, data) VALUES (?, ?)",
        [agentId, JSON.stringify(progressData)],
        (err) => {
          if (err) {
            this.logger.error("Store progress error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
  async storeMessage(message: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "INSERT INTO messages (id, from_agent, to_agent, content, priority, type, read_status, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
          message.id,
          message.from,
          message.to,
          message.content,
          message.priority,
          message.type,
          message.read ? 1 : 0,
          message.timestamp.toISOString(),
          message.metadata ? JSON.stringify(message.metadata) : null,
        ],
        (err) => {
          if (err) {
            this.logger.error("Store message error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
  async getMessagesForAgent(agentId: string) {
    return new Promise<any[]>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.all(
        "SELECT * FROM messages WHERE to_agent = ? ORDER BY timestamp DESC",
        [agentId],
        (err, rows) => {
          if (err) {
            this.logger.error("Get messages for agent error", err);
            reject(err);
          } else {
            const messages = (rows as any[]).map((msg: any) => ({
              id: msg.id,
              from: msg.from_agent,
              to: msg.to_agent,
              content: msg.content,
              priority: msg.priority,
              type: msg.type,
              read: msg.read_status === 1,
              timestamp: new Date(msg.timestamp),
              metadata: msg.metadata ? JSON.parse(msg.metadata) : null,
            }));
            resolve(messages);
          }
        },
      );
    });
  }
  async getRecentMessages(limit: number = 50) {
    return new Promise<any[]>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.all(
        "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?",
        [limit],
        (err, rows) => {
          if (err) {
            this.logger.error("Get recent messages error", err);
            reject(err);
          } else {
            const messages = (rows as any[]).map((msg: any) => ({
              id: msg.id,
              from: msg.from_agent,
              to: msg.to_agent,
              content: msg.content,
              priority: msg.priority,
              type: msg.type,
              read: msg.read_status === 1,
              timestamp: new Date(msg.timestamp),
              metadata: msg.metadata ? JSON.parse(msg.metadata) : null,
            }));
            resolve(messages);
          }
        },
      );
    });
  }
  async updateMessage(message: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "UPDATE messages SET read_status = ?, metadata = ? WHERE id = ?",
        [
          message.read ? 1 : 0,
          message.metadata ? JSON.stringify(message.metadata) : null,
          message.id,
        ],
        (err) => {
          if (err) {
            this.logger.error("Update message error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
  async storeQualityGate(qualityGate: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "INSERT OR REPLACE INTO quality_gates (id, name, description, type, status, criteria, last_run, next_run, agent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
          qualityGate.id,
          qualityGate.name,
          qualityGate.description,
          qualityGate.type,
          qualityGate.status,
          JSON.stringify(qualityGate.criteria),
          qualityGate.lastRun.toISOString(),
          qualityGate.nextRun.toISOString(),
          qualityGate.agentId,
        ],
        (err) => {
          if (err) {
            this.logger.error("Store quality gate error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
  async storeConflict(conflict: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "INSERT INTO conflicts (id, type, description, severity, agents, status, created_at, resolved_at, resolution, escalated_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
          conflict.id,
          conflict.type,
          conflict.description,
          conflict.severity,
          JSON.stringify(conflict.agents),
          conflict.status,
          conflict.createdAt.toISOString(),
          conflict.resolvedAt ? conflict.resolvedAt.toISOString() : null,
          conflict.resolution || null,
          conflict.escalatedTo || null,
        ],
        (err) => {
          if (err) {
            this.logger.error("Store conflict error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
  async updateConflict(conflict: any) {
    return new Promise<void>((resolve, reject) => {
      if (!this.db) {
        reject(new Error("Database not initialized"));
        return;
      }
      this.db.run(
        "UPDATE conflicts SET status = ?, resolved_at = ?, resolution = ?, escalated_to = ? WHERE id = ?",
        [
          conflict.status,
          conflict.resolvedAt ? conflict.resolvedAt.toISOString() : null,
          conflict.resolution || null,
          conflict.escalatedTo || null,
          conflict.id,
        ],
        (err) => {
          if (err) {
            this.logger.error("Update conflict error", err);
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }
}
