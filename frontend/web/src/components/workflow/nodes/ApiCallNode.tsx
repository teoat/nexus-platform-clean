import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const ApiCallNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.method &&
          data.config?.url &&
          `${data.config.method} ${data.config.url.substring(0, 25)}...`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#eb2f96" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#eb2f96" }}
      />
    </div>
  );
};

export default ApiCallNode;
