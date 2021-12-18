import difflib
import json
import sys
from enum import Enum


# 数字越大EQ程度越深
class CompareResult(Enum):
    NotEQ = 1
    MaybeEQ = 2
    Equal = 3


class Entity:
    def __init__(
        self,
        entityID: int,
        entityName: str,
        entityType: str,
        entityFile: str,
        startLine: int,
        startColumn: int,
        endLine: int,
        endColumn: int,
        dataset: str = None,
    ):
        self.entityID = entityID
        self.entityName = entityName
        self.entityType = entityType
        self.entityFile = entityFile
        self.startLine = startLine
        self.startColumn = startColumn
        self.endLine = endLine
        self.endColumn = endColumn
        self.dataset = dataset

    def into_dict(self):
        return {
            'entityID': self.entityID,
            'entityName': self.entityName,
            'entityType': self.entityType,
            'entityFile': self.entityFile,
            'startLine': self.startLine,
            'startColumn': self.startColumn,
            'endLine': self.endLine,
            'endColumn': self.endColumn,
            'dataset': self.dataset
        }

    @staticmethod
    def construct(source, dataset=None):
        return Entity(
            source['entityID'],
            source['entityName'],
            source['entityType'],
            source['entityFile'],
            source['startLine'],
            source['startColumn'],
            source['endLine'],
            source['endColumn'],
            dataset
        )


class Dependency:
    def __init__(self, dependencyType, dependencySrcID, dependencyDestID, startLine, startColumn, endLine, endColumn, dataset=None):
        self.dependencyType = dependencyType
        self.dependencySrcID = dependencySrcID
        self.dependencyDestID = dependencyDestID
        self.startLine = startLine
        self.startColumn = startColumn
        self.endLine = endLine
        self.endColumn = endColumn

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
            source['dependencyDestID'],
            source['startLine'],
            source['startColumn'],
            source['endLine'],
            source['endColumn'],
            dataset
        )


# 抽象类：比较器
# 其实相当于是比较函数，比较返回EQ程度
# class Comparer:
#     def compare(self, lhs, rhs):
#         pass


# 处理器 集成Comparer和L_SET、R_SET，利用比较器对左右集合进行比较
class Handler:
    def __init__(self, comparer, l_set: list[Entity], r_set: list[Entity]):
        self.comparer = comparer
        self.l_set = l_set
        self.r_set = r_set
        pass

    def work(self):
        contains = set()
        eq_set = set()
        maybe_eq_set = set()
        ne_set = set()

        for lhs in self.l_set:
            for rhs in self.r_set:
                cmp_result = self.comparer.compare(lhs, rhs)
                if cmp_result == CompareResult.Equal:
                    contains.add(lhs)
                    contains.add(rhs)
                    eq_set.add((lhs, rhs))
                elif cmp_result == CompareResult.MaybeEQ:
                    contains.add(lhs)
                    contains.add(rhs)
                    maybe_eq_set.add((lhs, rhs))
                elif cmp_result == CompareResult.NotEQ:
                    # do nothing
                    pass
        for lhs in self.l_set:
            if lhs not in contains:
                ne_set.add(lhs)
        for rhs in self.r_set:
            if rhs not in contains:
                ne_set.add(rhs)

        return eq_set, maybe_eq_set, ne_set


# 解析命令行参数 原封不动的搬过来，虽然知道python有自己的解析库
def parse_param(label):
    for arg in sys.argv:
        if arg.startswith(f'--{label}='):
            return arg.split('=')[1]
        else:
            continue
    return None


# 调用difflib，查看两个字符串的相似度
def string_equal_rate(str1: str, str2: str):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


# 判断str2是否是str1的子串
# 如果str2包含多个数据，那么判断str2中是否存在str1的子串
def string_contains(str1: str, *str2: str):
    for i in str2:
        if str1.find(i) != -1:
            return True
    return False


# 具体类：比较Code2Graph和Depends的Node的比较函数
# 非常简易，如果完全相等，就返回相等
class Code2Graph_Depends_EntityComparer:
    def compare(self, lhs: Entity, rhs: Entity):
        if lhs.entityType.upper() == 'FILE' and rhs.entityType.upper() == 'FILE':
            # 获取每一级的路径
            sourcetrail_token_vector = [each for each in filter(
                lambda x: x != '', lhs.entityName.split('.'))].reverse()
            depends_token_vector = rhs.entityName.replace(
                '\\', '/').split('/').reverse()
            # 对比结果 严格对比，有一点不一样就返回NotEQ
            for i, j in zip(sourcetrail_token_vector, depends_token_vector):
                if i != j:
                    return CompareResult.NotEQ
            return CompareResult.Equal
        elif lhs.entityType.upper() in ['ENUM', 'CLASS'] and rhs.entityType.upper() == 'TYPE':
            pass
        elif lhs.entityType.upper() == 'METHOD' and rhs.entityType.upper() == 'FUNCTION':
            pass
        elif lhs.entityType.upper() == 'VARIABLE' and rhs.entityType.upper() == 'VAR':
            pass
        else:
            return CompareResult.NotEQ


class Understand_Depends_EntityComparer:
    def compare(self, lhs: Entity, rhs: Entity):
        if (
            string_contains(lhs.entityType.upper(), 'PACKAGE')
                and rhs.entityType.upper() == 'PACKAGE'
            or string_contains(lhs.entityType.upper(), 'ENUM', 'CLASS')
                and rhs.entityType.upper() == 'TYPE'
            or string_contains(lhs.entityType.upper(), 'METHOD')
                and rhs.entityType.upper() == 'FUNCTION'
            or string_contains(lhs.entityType.upper(), 'VARIABLE')
                and rhs.entityType.upper() == 'VAR'
        ):
            if lhs.entityName == rhs.entityName:
                return CompareResult.Equal
            else:
                return CompareResult.NotEQ
        else:
            return CompareResult.NotEQ


class ENRE_Depends_EntityComparer:
    def compare(self, lhs: Entity, rhs: Entity):
        if (
            lhs.entityType.upper() == 'PACKAGE'
                and rhs.entityType.upper() == 'PACKAGE'
            or lhs.entityType.upper() == 'FILE'
                and rhs.entityType.upper() == 'FILE'
            or string_contains(lhs.entityType.upper(), 'ANNOTATION')
                and rhs.entityType.upper() == 'ANNOTATION'
            or string_contains(lhs.entityType.upper(), 'ENUM', 'CLASS', 'INTERFACE')
                and rhs.entityType.upper() == 'TYPE'
            or lhs.entityType.upper() == 'VARIABLE'
                and rhs.entityType.upper() == 'VAR'
        ):
            if lhs.entityName == rhs.entityName:
                return CompareResult.Equal
            else:
                return CompareResult.NotEQ
        return CompareResult.NotEQ


class ENRE_Understand_EntityComparer:
    def compare(self, lhs: Entity, rhs: Entity):
        if (
            lhs.entityType.upper().endswith('PACKAGE')
                and rhs.entityType.upper().endswith('PACKAGE')
            or lhs.entityType.upper().endswith('METHOD')
                and rhs.entityType.upper().endswith('METHOD')
            or lhs.entityType.upper().endswith('VARIABLE')
                and rhs.entityType.upper().endswith('VARIABLE')
            or lhs.entityType.upper().endswith('INTERFACE')
                and rhs.entityType.upper().endswith('INTERFACE')
            or lhs.entityType.upper().endswith('ENUM')
                and rhs.entityType.upper().endswith('ENUM')
            or lhs.entityType.upper().endswith('CLASS')
                and rhs.entityType.upper().endswith('CLASS')
        ):
            if lhs.entityName == rhs.entityName:
                print(lhs.entityName)
                return CompareResult.Equal
            else:
                return CompareResult.NotEQ
        return CompareResult.NotEQ
'''
python differ.py --ltype=enre --lhs=./halo/enre_halo_entity.json --rtype=understand --rhs=./halo/understand_halo_entity.json --compare=entity --output=./enre_understand_entity_output.json
'''


class Sourcetrail_Depends_EntityComparer:
    def compare(self, lhs: Entity, rhs: Entity):
        # token vector是指关键字的数组，用于判断数据是否一致
        sourcetrail_token_vector = None
        depends_token_vector = None

        if lhs.entityType.upper == 'FILE' and rhs.entityType.upper == 'FILE':
            # 获取每一级的路径
            sourcetrail_token_vector = lhs.entityName.replace(
                '\\', '/').split('/')
            depends_token_vector = rhs.entityName.replace('\\', '/').split('/')
            # 对比结果 严格对比，有一点不一样就返回NotEQ
            for i, j in zip(sourcetrail_token_vector, depends_token_vector):
                if i != j:
                    return CompareResult.NotEQ
            return CompareResult.Equal
        elif lhs.entityType.upper == 'PACKAGE' and rhs.entityType.upper == 'PACKAGE':
            if lhs.entityName[1:] == rhs.entityName:
                return CompareResult.Equal
            else:
                return CompareResult.NotEQ
        elif lhs.entityType.upper == 'METHOD' and rhs.entityType.upper == 'FUNCTION':
            eq_rate = string_equal_rate(lhs.entityName, rhs.entityName)
            if eq_rate >= 0.95:
                return CompareResult.Equal
            elif 0.9 < eq_rate < 0.95:
                return CompareResult.MaybeEQ
            else:
                return CompareResult.NotEQ
            # return CompareResult.NotEQ
        elif (
            lhs.entityType.upper in ['INTERFACE', 'CLASS',
                                     'PUBLIC CLASS', 'ENUM', 'ANNOTATION']
            and rhs.entityType.upper == 'TYPE'
        ):
            sourcetrail_token_vector = []
            depends_token_vector = []
            # 状态机：抛弃泛型参数
            state = 'scanning'
            current = ''
            for i, each in enumerate(lhs.entityName):
                if each == '<':
                    state = 'dispose generic'
                elif each == '>':
                    state = 'scanning'
                elif state == 'scanning':
                    current += each
            sourcetrail_token_vector = [x for x in filter(
                lambda x: x != '', current.split('.'))]
            # 状态机：抛弃泛型参数
            state = 'scanning'
            current = ''
            for i, each in enumerate(rhs.entityName):
                if each == '<':
                    state = 'dispose generic'
                elif each == '>':
                    state = 'scanning'
                elif state == 'scanning':
                    current += each
            depends_token_vector = [x for x in filter(
                lambda x: x != '', current.split('.'))]
            # print(f'l: {sourcetrail_token_vector}, r: {depends_token_vector}')
            if len(sourcetrail_token_vector) != len(depends_token_vector):
                return CompareResult.NotEQ
            for i, j in zip(sourcetrail_token_vector, depends_token_vector):
                if i != j:
                    return CompareResult.NotEQ
            return CompareResult.Equal
        else:
            return CompareResult.NotEQ


class Dependency_EntityComparer:
        def compare(self, lhs: Dependency, rhs: Dependency):
            lhs.dependencySrcID


def main():
    L_INPUT = parse_param('lhs')
    R_INPUT = parse_param('rhs')
    L_TYPE = parse_param('ltype')
    R_TYPE = parse_param('rtype')
    COMPARE_TYPE = parse_param('compare')
    OUTPUT_FILE = parse_param('output')

    # 为生成handler做准备
    comparer = None
    # 为每种情况做一个处理，当然解耦合的情况就是搞一个对象映射，启动的时候对这个映射进行注册
    # 然后用依赖注入来做，但是这里具体的需求不需要解耦合
    if L_TYPE == 'code2graph' and R_TYPE == 'depends' and COMPARE_TYPE == 'entity':
        comparer = Code2Graph_Depends_EntityComparer()
    elif L_TYPE == 'sourcetrail' and R_TYPE == 'depends' and COMPARE_TYPE == 'entity':
        comparer = Sourcetrail_Depends_EntityComparer()
    elif L_TYPE == 'understand' and R_TYPE == 'depends' and COMPARE_TYPE == 'entity':
        comparer = Understand_Depends_EntityComparer()
    elif L_TYPE == 'enre' and R_TYPE == 'depends' and COMPARE_TYPE == 'entity':
        comparer = ENRE_Depends_EntityComparer()
    elif L_TYPE == 'enre' and R_TYPE == 'understand' and COMPARE_TYPE == 'entity':
        comparer = ENRE_Understand_EntityComparer()

    lset = []
    rset = []
    with open(L_INPUT) as f:
        input = json.load(f)
        if COMPARE_TYPE == 'dependency':
            lset = [Dependency.construct(each, L_TYPE)
                    for each in input[COMPARE_TYPE]]
        elif COMPARE_TYPE == 'entity':
            lset = [Entity.construct(each, L_TYPE)
                    for each in input[COMPARE_TYPE]]
    with open(R_INPUT) as f:
        input = json.load(f)
        if COMPARE_TYPE == 'dependency':
            rset = [Dependency.construct(each, R_TYPE)
                    for each in input[COMPARE_TYPE]]
        elif COMPARE_TYPE == 'entity':
            rset = [Entity.construct(each, R_TYPE)
                    for each in input[COMPARE_TYPE]]

    map = dict()
    for i in lset:
        if i.entityType in map:
            map[i.entityType] = map[i.entityType] + 1
        else:
            map[i.entityType] = 1
    for i in rset:
        if i.entityType in map:
            map[i.entityType] = map[i.entityType] + 1
        else:
            map[i.entityType] = 1
    print(f'map: {map}')
    # 生成Handler对象
    handler = Handler(comparer, lset, rset)
    # 获得结果
    eq_set, maybe_eq_set, ne_set = handler.work()
    # 输出结果
    with open(OUTPUT_FILE, 'w') as output:
        result = {
            'eq': [(each[0].into_dict(), each[1].into_dict()) for each in eq_set],
            'maybe_eq': [(each[0].into_dict(), each[1].into_dict()) for each in maybe_eq_set],
            'ne': [each.into_dict() for each in ne_set],
        }
        json.dump(result, output, indent=4)
    # 打印部分数据
    print({
        'eq': len(eq_set),
        'maybe_eq': len(maybe_eq_set),
        'ne': len(ne_set),
    })


if __name__ == '__main__':
    main()
