import argparse
import csv
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tool", type=str, required=True, choices=['enre', 'understand', 'sourcetrail', 'depends'],
                        help="choose the tool you used, eg: understand, enre, depends...")
    parser.add_argument("-e", "--entityInput", type=str, required=True, help="please input the input entity file path")
    parser.add_argument("-d", "--dependencyInput", type=str, required=True, help="please input the input dependency file path")
    parser.add_argument("-p", "--projectname", type=str, required=True, help="please input the project name")
    parser.add_argument("-o", "--output", type=str, required=True, help="please input the output file path")
    args = parser.parse_args()
    return args.tool, args.entityInput, args.dependencyInput, args.projectname, args.output


def output_file(cell: dict, json_path: str, projectname:str, type:str):
    info = dict()
    info["schemaVersion"] = 1.0
    info[type] = cell
    info['projectName'] = projectname
    entity_str = json.dumps(info, indent=4)
    with open(json_path, 'w') as json_file:
        json_file.write(entity_str)


def Entity(entityID, entityName, entityType, entityFile = None, startLine = -1, startColumn = -1, endLine = -1, endColumn = -1):
    entity = dict()
    entity['entityID'] = entityID
    entity['entityName'] = entityName
    entity['entityType'] = entityType
    entity['entityFile'] = entityFile
    entity['startLine'] = startLine
    entity['startColumn'] = startColumn
    entity['endLine'] = endLine
    entity['endColumn'] = endColumn
    return entity


def Dependency(dependencyType, dependencySrcID, dependencydestID, startLine = -1, startColumn = -1, endLine = -1, endColumn = -1):
    dependency = dict()
    dependency['dependencyType'] = dependencyType
    dependency['dependencySrcID'] = dependencySrcID
    dependency['dependencyDestID'] = dependencydestID
    dependency['startLine'] = startLine
    dependency['startColumn'] = startColumn
    dependency['endLine'] = endLine
    dependency['endColumn'] = endColumn
    return dependency


def enre_format(path: str, projectname:str, output:str):
    with open(path, 'r', encoding='utf-8') as understand_file:
        enre_result = json.load(understand_file)
    nodes = enre_result['variables']
    edges = enre_result['cells']

    node_count = list()
    edge_count = list()

    for node in nodes:
        if node['external'] == True:
            break
        node_count.append(Entity(node['id'], node['qualifiedName'], node['category']))
    for edge in edges:
        values = edge['values']
        for value in values.keys():
            type = value
        edge_count.append(Dependency(type, edge['src'], edge['dest']))
    output_file(node_count, output+"/enre_"+projectname+"_entity.json", projectname, "entity")
    output_file(edge_count, output+"/enre_"+projectname+"_dependency.json", projectname, "dependency")


def understand_format(entity_path: str, dependency_path:str, projectname:str, output:str):
    with open(dependency_path, 'r', encoding='utf-8') as understand_file:
        understand_edge = json.load(understand_file)
    edges = understand_edge['cells']
    edge_count = list()
    for edge in edges:
        details = edge['details']
        for detail in details:
            src = detail['src']
            dest = detail['dest']
            edge_count.append(Dependency(detail['type'], src['object'], dest['object']))
    output_file(edge_count, output + "/understand_" + projectname + "_dependency.json", projectname, "dependency")


def sourcetrail_format(entity_path: str, dependency_path:str, projectname:str, output:str):
    entity_dict = {"1": "symbol", "4": "built-in", "16": "namespace", "32": "package",
                   "128": "public class", "256": "interface", "512": "Annotation",
                   "1024": "global variable", "2048": "field", "4096": "function",
                   "8192": "method", "16384": "enum", "32768": "enumerator", "65536": "typedef",
                   "131072": "class", "262144": "file", "524144": "macro", "1048576": "union"}

    dependency_dict = {"1": "scope resolve", "2": "type use", "4": "use", "8": "call",
                       "16": "extend", "32": "override", "64": "type argument",
                       "256": "include", "512": "import", "2048": "macro use",
                       "4096": "annotation use"}
    csvFile = open(entity_path, "r")
    dict_reader = csv.DictReader(csvFile)

    node_list = list()
    for row in dict_reader:
        if row['serialized_name'].__contains__("	s	p"):
            row['serialized_name'] = row['serialized_name'].replace("	s	p", "")
        if row['serialized_name'].__contains__("/	m"):
            row['serialized_name'] = row['serialized_name'].replace("/	m", "")
        if row['serialized_name'].__contains__("::	m.:main:."):
            row['serialized_name'] = row['serialized_name'].replace("::	m.:main:.", "")
        if row['serialized_name'].__contains__("::    m"):
            row['serialized_name'] = row['serialized_name'].replace("::    m", "")
        if row['serialized_name'].__contains__("\tn"):
            row['serialized_name'] = row['serialized_name'].replace("\tn", ".")
        if row['serialized_name'].__contains__("\tm"):
            row['serialized_name'] = row['serialized_name'].replace("\tm", "")
        if row['serialized_name'].__contains__("\ts"):
            row['serialized_name'] = row['serialized_name'].replace("\ts", "")
        if row['serialized_name'].__contains__("\tp"):
            row['serialized_name'] = row['serialized_name'].replace("\tp", "")
        if row['type'] in entity_dict.keys():
            type = entity_dict[row['type']]
        else:
            type = None
            print(row['type'])
            print(row['serialized_name'])
        node_list.append(Entity(int(row['id']), row['serialized_name'], type))
    output_file(node_list, output + "/sourcetrail_" + projectname + "_entity.json", projectname, "entity")


    csvFile = open(dependency_path, "r")
    dict_reader = csv.DictReader(csvFile)
    edge_list = list()
    for row in dict_reader:
        if row['type'] in dependency_dict.keys():
            type = dependency_dict[row['type']]
        else:
            type = None
            print(row['type'])
            print(row)
        edge_list.append(Dependency(type, int(row['source_node_id']), int(row['target_node_id'])))
    output_file(edge_list, output + "/sourcetrail_" + projectname + "_dependency.json", projectname, "dependency")


def depends_format(entity_path: str, dependency_path:str, projectname:str, output:str):
    with open(entity_path, 'r', encoding='utf-8') as txtfile:
        nodes = txtfile.read()
    node_list = nodes.split("\n")
    node_count = list()
    for node in node_list:
        node_info = node.split("/")
        if len(node_info) >= 3:
            type = node_info[2].split(".")[-1]
            type = type.replace("Entity", "")
            node_count.append(Entity(int(node_info[0]),  node_info[1], type))
    output_file(node_count, output + "/depends_" + projectname + "_entity.json", projectname, "entity")
    with open(dependency_path, 'r', encoding='utf-8') as depends_file:
        depends_edge = json.load(depends_file)
    edge_count = list()
    for cell in depends_edge['cells']:
        values = cell['values']
        for value in values.keys():
            edge_count.append(Dependency(value, cell['src'], cell['dest']))
    output_file(edge_count, output + "/depends_" + projectname + "_dependency.json", projectname, "dependency")


if __name__ == "__main__":
    tool, entityInput, dependencyInput, projectname, output = parse_args()
    if tool == "enre":
        enre_format(entityInput, projectname, output)
    if tool == "understand":
        understand_format(entityInput, dependencyInput, projectname, output)
    if tool == "sourcetrail":
        sourcetrail_format(entityInput, dependencyInput, projectname, output)
    if tool == "depends":
        depends_format(entityInput, dependencyInput, projectname, output)