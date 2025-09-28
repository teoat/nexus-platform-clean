import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { CoordinationHub } from './core/CoordinationHub';
import { AgentManager } from './core/AgentManager';
import { TaskScheduler } from './core/TaskScheduler';
import { CommunicationEngine } from './core/CommunicationEngine';
import { QualityGateManager } from './core/QualityGateManager';
import { ConflictResolver } from './core/ConflictResolver';
import { DatabaseManager } from './core/DatabaseManager';
import { Logger } from './utils/Logger';

dotenv.config();

class NexusCoordinationServer {
  private app: express.Application;
  private server: any;
  private io: Server;
  private coordinationHub: CoordinationHub;
  private logger: Logger;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.io = new Server(this.server, {
      cors: {
        origin: process.env.CORS_ORIGIN?.split(',') || ["http://localhost:3000", "http://localhost:3001"],
        methods: ["GET", "POST"]
      }
    });
    this.logger = new Logger();
    this.coordinationHub = new CoordinationHub();
  }

  private setupMiddleware() {
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.CORS_ORIGIN?.split(',') || ["http://localhost:3000", "http://localhost:3001"],
      credentials: true
    }));
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    this.app.use((req, res, next) => {
      this.logger.info(`${req.method} ${req.path}`, {
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });
      next();
    });
  }

  private setupRoutes() {
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: '1.0.0'
      });
    });

    this.app.use('/api/coordination', this.coordinationHub.getRouter());

    this.io.on('connection', (socket) => {
      this.logger.info('New WebSocket connection', { socketId: socket.id });

      socket.on('auth', (data) => {
        this.coordinationHub.authenticateSocket(socket, data);
      });

      socket.on('disconnect', () => {
        this.logger.info('WebSocket disconnected', { socketId: socket.id });
      });
    });
  }

  async start(port: number = 8000) {
    try {
      this.setupMiddleware();
      this.setupRoutes();

      await this.coordinationHub.initialize();

      this.server.listen(port, () => {
        this.logger.info(`Nexus Coordination Server running on port ${port}`);
      });
    } catch (error) {
      this.logger.error('Failed to start server', { error });
      process.exit(1);
    }
  }
}

// Start the server
const server = new NexusCoordinationServer();
server.start().catch(console.error);