import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const TimerNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.delay_seconds && `Delay: ${data.config.delay_seconds}s`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#a0d911" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#a0d911" }}
      />
    </div>
  );
};

export default TimerNode;
