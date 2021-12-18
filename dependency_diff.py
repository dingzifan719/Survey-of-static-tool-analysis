import argparse
import json
from enum import Enum


class CompareResult(Enum):
    NotEQ = -1
    Equal = 1


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-lt", "--left_tool", type=str, required=True, choices=['enre', 'understand', 'sourcetrail', 'depends', 'code2graph'],
                        help="choose the left tool you used, eg: understand, enre, depends...")
    parser.add_argument("-rt", "--right_tool", type=str, required=True,
                        choices=['enre', 'understand', 'sourcetrail', 'depends', 'code2graph'],
                        help="choose the right tool you used, eg: understand, enre, depends...")
    parser.add_argument("-e", "--entity", type=str, required=True, help="please input the entity file path")
    parser.add_argument("-ld", "--left_dependency", type=str, required=True, help="please input the left dependency file path")
    parser.add_argument("-rd", "--right_dependency", type=str, required=True, help="please input the right dependency file path")
    parser.add_argument("-p", "--projectname", type=str, required=True, help="please input the project name")
    parser.add_argument("-o", "--output", type=str, required=True, help="please input the output file path")
    args = parser.parse_args()
    return args.left_tool, args.right_tool, args.entity,  \
           args.left_dependency, args.right_dependency, args.projectname, args.output


class Dependency:
    def __init__(self, dependencyType, dependencySrcID, dependencyDestID, startLine, startColumn, endLine, endColumn, dataset=None):
        self.dependencyType = dependencyType
        self.dependencySrcID = dependencySrcID
        self.dependencyDestID = dependencyDestID
        self.startLine = startLine
        self.startColumn = startColumn
        self.endLine = endLine
        self.endColumn = endColumn
        self.dataset = dataset

    def into_dict(self):
        return {
            'dependencyType': self.dependencyType,
            'dependencySrcID': self.dependencySrcID,
            'dependencyDestID': self.dependencyDestID,
            'startLine': self.startLine,
            'startColumn': self.startColumn,
            'endLine': self.endLine,
            'endColumn': self.endColumn,
            'dataset': self.dataset
        }

    @staticmethod
    def construct(source, dataset=None):
        return Dependency(
            source['dependencyType'],
            source['dependencySrcID'],
            source['dependencydestID'],
            source['startLine'],
            source['startColumn'],
            source['endLine'],
            source['endColumn'],
            dataset
        )


# 处理器 集成Comparer和L_SET、R_SET，利用比较器对左右集合进行比较
class Handler:
    def __init__(self, comparer, l_set: dict[int: Dependency], r_set: dict[int: Dependency], eq_info: dict):
        self.comparer = comparer
        self.l_set = l_set
        self.r_set = r_set
        self.eq_info = eq_info
        pass

    def work(self):
        eq_set = set()
        ne_set = set()

        eq = 0
        eq_dict = dict()
        for l_src in self.l_set.keys():
            if l_src in self.eq_info.keys():
                # 首先去匹配两个工具的src
                dest1_2 = dict()
                for l_dest_dep in self.l_set[l_src]:
                    # 通过获得到src来找工具1的dest， 将工具1的dest映射到工具2的实体ID
                    if l_dest_dep.dependencyDestID in self.eq_info.keys():
                        dest1_2[self.eq_info[l_dest_dep.dependencyDestID]] = l_dest_dep
                r_src = self.eq_info[l_src]
                if r_src not in r_set.keys():
                    continue
                for r_dest_dep in self.r_set[r_src]:
                    if r_dest_dep.dependencyDestID in dest1_2:
                        eq_set.add((dest1_2[r_dest_dep.dependencyDestID], r_dest_dep))
        return eq_set, ne_set




dependency_dict = {
    'code2graph': {'parameter': 'PARAMETER', 'annotation': 'ANNOTATE',
                   'caller': 'CALL', 'casted_object': 'CAST'},
    'enre': {'Parameter': 'PARAMETER', 'Annotate': 'ANNOTATE', 'Import': 'IMPORT',
             'Use': 'USE', 'Set': 'SET', 'Cast': 'CAST', 'Implement': 'IMPLEMENT',
             'Inherit': 'EXTEND', 'Call': 'CALL', 'Call non-dynamic': 'CALL'},
    'sourcetrail': {'import': 'IMPORT', 'annotation use': 'USE', 'use': 'USE',
                    'type use': 'USE', 'extend': 'EXTEND', 'override': 'OVERRIDE',
                    'call': 'CALL'},
    'understand': {'Use': 'USE', 'Import': 'IMPORT', 'Call': 'CALL',
                   'Extend': 'EXTEND', 'Implement': 'IMPLEMENT', 'Cast': 'CAST',
                   'Use Partial': 'USE', 'Set': 'SET', 'import': 'IMPORT'}
}


def get_dep_info(path: str, tool: str):
    # 读取依赖信息
    with open(path, 'r', encoding='utf-8') as json_file:
        info = json.load(json_file)
    dep_info = dict()
    for dep in info['dependency']:
        if dep['dependencySrcID'] not in dep_info.keys():
            dep_list = list()
        else:
            dep_list = dep_info[dep['dependencySrcID']]
        dep_list.append(Dependency.construct(dep, tool))
        dep_info[dep['dependencySrcID']] = dep_list
    return dep_info


def get_dep(l_dep: str, l_tool:str, r_dep: str, r_tool:str):
    return get_dep_info(l_dep, l_tool), get_dep_info(r_dep, r_tool)


class Dependency_Comparer:
        def compare(self, lhs: Dependency, rhs: Dependency, eq: dict()):
            lhs.dependencySrcID



def get_entity_output_info(path: str, dataset1:str):
    # 读取实体相似性分析结果
    with open(path, 'r', encoding='utf-8') as json_file:
        info = json.load(json_file)
    info_dict = dict()
    for entity_tuple in info['eq']:
        src = dest = 0
        for entity in entity_tuple:
            if entity['dataset'] == dataset1:
                src = entity['entityID']
            else:
                dest = entity['entityID']
        info_dict[src] = dest
    return info_dict


def dep_analyzer(dep_info1: dict, dep_info2: dict, eq_info: dict, maybe_eq_info: dict):
    eq = 0
    eq_dict = dict()
    for src1 in dep_info1.keys():
        if src1 in eq_info.keys():
        # 首先去匹配两个工具的src
            dest1_2 = set()
            for dest1 in dep_info1[src1]:
                # 通过获得到src来找工具1的dest， 将工具1的dest映射到工具2的实体ID
                if dest1[0] in eq_info.keys():
                    dest1_2.add(eq_info[dest1[0]])
            src2 = eq_info[src1]
            if src2 not in dep_info2.keys():
                continue
            for dest2 in dep_info2[src2]:
                if dest2[0] in dest1_2:
                    if dest2[1] not in eq_dict.keys():
                        eq_dict[dest2[1]] = 1
                    else:
                        eq_dict[dest2[1]] =  eq_dict[dest2[1]] + 1



if __name__ == "__main__":
    L_TOOL, R_TOOL, ENTITY, L_DEP, R_DEP, PROJECTNAME, OUTPUT = parse_args()
    comparer = Dependency_Comparer()
    l_set, r_set = get_dep(L_DEP, L_TOOL, R_DEP, R_TOOL)
    eq_info = get_entity_output_info(ENTITY, L_TOOL)


    handler = Handler(comparer, l_set, r_set, eq_info)

    eq_set,  ne_set = handler.work()
    with open(OUTPUT, 'w') as output:
        result = {
            'eq': [(each[0].into_dict(), each[1].into_dict()) for each in eq_set],
        }
        json.dump(result, output, indent=4)
        # 打印部分数据
    print({
        'eq': len(eq_set),
    })