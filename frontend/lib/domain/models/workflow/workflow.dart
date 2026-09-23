import 'workflow_edge.dart';
import 'workflow_node.dart';

class Workflow {
  final List<WorkflowNode> nodes;
  final List<WorkflowEdge> edges;

  const Workflow({this.nodes = const [], this.edges = const []});

  WorkflowNode? getNode(String nodeId) {
    for (final node in nodes) {
      if (node.id == nodeId) {
        return node;
      }
    }

    return null;
  }

  List<WorkflowNode> startNodes() {
    final destinations = <String>{};

    for (final edge in edges) {
      destinations.add(edge.toNode);
    }

    for (final node in nodes) {
      for (final dependency in node.dependsOn) {
        if (dependency.isNotEmpty) {
          destinations.add(dependency);
        }
      }
    }

    return nodes.where((node) => !destinations.contains(node.id)).toList();
  }

  List<WorkflowNode> parents(String nodeId) {
    final node = getNode(nodeId);

    if (node == null) {
      return [];
    }

    final parentIds = <String>{};

    for (final edge in edges) {
      if (edge.toNode == nodeId) {
        parentIds.add(edge.fromNode);
      }
    }

    parentIds.addAll(node.dependsOn);

    return nodes.where((node) => parentIds.contains(node.id)).toList();
  }

  List<WorkflowNode> children(String nodeId) {
    final childIds = <String>{};

    for (final edge in edges) {
      if (edge.fromNode == nodeId) {
        childIds.add(edge.toNode);
      }
    }

    for (final node in nodes) {
      if (node.dependsOn.contains(nodeId)) {
        childIds.add(node.id);
      }
    }

    return nodes.where((node) => childIds.contains(node.id)).toList();
  }

  List<WorkflowEdge> incomingEdges(String nodeId) {
    return edges.where((edge) => edge.toNode == nodeId).toList();
  }

  List<WorkflowEdge> outgoingEdges(String nodeId) {
    return edges.where((edge) => edge.fromNode == nodeId).toList();
  }

  int get totalNodes => nodes.length;

  int get totalEdges => edges.length;

  bool get isEmpty => nodes.isEmpty;

  bool contains(String nodeId) {
    return getNode(nodeId) != null;
  }
}
