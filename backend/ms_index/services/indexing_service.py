import os
import git
import tempfile
import shutil
from typing import Dict, List, Any
from pathlib import Path
import re
import ast
import javalang
from ..app import DependencyGraphData, DependencyNode, DependencyEdge

class IndexingService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="impact_analyzer_")
    
    async def clone_repository(self, repo_url: str, commit_hash: str) -> str:
        """Clone repository to temporary directory"""
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(self.temp_dir, repo_name)
        
        try:
            # Clone repository
            repo = git.Repo.clone_from(repo_url, repo_path)
            
            # Checkout specific commit
            repo.git.checkout(commit_hash)
            
            return repo_path
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    async def parse_code_structure(self, repo_path: str, dependency_graph: DependencyGraphData) -> DependencyGraphData:
        """Parse code structure and enhance dependency graph"""
        enhanced_nodes = list(dependency_graph.nodes)
        enhanced_edges = list(dependency_graph.edges)
        
        # Parse Java files
        java_files = self._find_java_files(repo_path)
        java_classes = self._parse_java_files(java_files)
        
        # Parse TypeScript/Angular files
        ts_files = self._find_typescript_files(repo_path)
        ts_components = self._parse_typescript_files(ts_files)
        
        # Add discovered classes as nodes
        for class_info in java_classes:
            enhanced_nodes.append(DependencyNode(
                id=class_info['name'],
                name=class_info['name'],
                type='class'
            ))
            
            # Add dependencies as edges
            for dependency in class_info['dependencies']:
                enhanced_edges.append(DependencyEdge(
                    from_node=class_info['name'],
                    to=dependency,
                    type='imports'
                ))
        
        # Add TypeScript components
        for component_info in ts_components:
            enhanced_nodes.append(DependencyNode(
                id=component_info['name'],
                name=component_info['name'],
                type='component'
            ))
            
            for dependency in component_info['dependencies']:
                enhanced_edges.append(DependencyEdge(
                    from_node=component_info['name'],
                    to=dependency,
                    type='imports'
                ))
        
        return DependencyGraphData(nodes=enhanced_nodes, edges=enhanced_edges)
    
    def _find_java_files(self, repo_path: str) -> List[str]:
        """Find all Java files in the repository"""
        java_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files
    
    def _find_typescript_files(self, repo_path: str) -> List[str]:
        """Find all TypeScript files in the repository"""
        ts_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.ts') and not file.endswith('.d.ts'):
                    ts_files.append(os.path.join(root, file))
        return ts_files
    
    def _parse_java_files(self, java_files: List[str]) -> List[Dict[str, Any]]:
        """Parse Java files to extract class information"""
        classes = []
        
        for file_path in java_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse Java file
                try:
                    tree = javalang.parse.parse(content)
                    
                    for path, node in tree.filter(javalang.tree.ClassDeclaration):
                        class_name = node.name
                        dependencies = []
                        
                        # Extract imports
                        if tree.imports:
                            for imp in tree.imports:
                                if imp.path:
                                    dependencies.append(imp.path.split('.')[-1])
                        
                        classes.append({
                            'name': class_name,
                            'file_path': file_path,
                            'dependencies': dependencies,
                            'type': 'class'
                        })
                        
                except javalang.parser.JavaSyntaxError:
                    # Fallback to regex parsing
                    class_matches = re.findall(r'class\s+(\w+)', content)
                    import_matches = re.findall(r'import\s+([^;]+);', content)
                    
                    for class_name in class_matches:
                        dependencies = [imp.split('.')[-1] for imp in import_matches]
                        classes.append({
                            'name': class_name,
                            'file_path': file_path,
                            'dependencies': dependencies,
                            'type': 'class'
                        })
                        
            except Exception as e:
                print(f"Error parsing Java file {file_path}: {e}")
                continue
        
        return classes
    
    def _parse_typescript_files(self, ts_files: List[str]) -> List[Dict[str, Any]]:
        """Parse TypeScript files to extract component information"""
        components = []
        
        for file_path in ts_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract component/service names
                component_matches = re.findall(r'export\s+class\s+(\w+)', content)
                import_matches = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
                
                for component_name in component_matches:
                    dependencies = [imp.split('/')[-1] for imp in import_matches if not imp.startswith('.')]
                    components.append({
                        'name': component_name,
                        'file_path': file_path,
                        'dependencies': dependencies,
                        'type': 'component'
                    })
                    
            except Exception as e:
                print(f"Error parsing TypeScript file {file_path}: {e}")
                continue
        
        return components