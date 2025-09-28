import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const DatabaseQueryNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.query &&
          `Query: ${data.config.query.substring(0, 20)}...`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#52c41a" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#52c41a" }}
      />
    </div>
  );
};

export default DatabaseQueryNode;
