import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const DataOutputNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.output_key && `Key: ${data.config.output_key}`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#722ed1" }}
      />
    </div>
  );
};

export default DataOutputNode;
