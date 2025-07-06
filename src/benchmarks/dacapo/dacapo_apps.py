# dacapo_apps.py
import os
from abc import ABC, abstractmethod

class DaCapoApp(ABC):
    def __init__(self, user_prefix):
        self.user_prefix = user_prefix

    @abstractmethod
    def get_source_path(self, class_name, namespace_name, group_name):
        pass

    @abstractmethod
    def get_test_info_from_parts(self, parts, test_class):
        pass

    @abstractmethod
    def get_build_dir(self, group_name):
        pass

    @abstractmethod
    def get_makefile_subfolders(self):
        pass

class FopApp(DaCapoApp):
    def __init__(self, user_prefix):
        super().__init__(user_prefix)
        self.root_dir = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/fop/build/fop-2.8/fop-core"
        self.src_dir = f"{self.root_dir}/src/main/java/org/apache/fop"

    def get_source_path(self, class_name, namespace_name, group_name):
        if namespace_name:
            return f"{self.src_dir}/{namespace_name}/{class_name}.java"
        return f"{self.src_dir}/{class_name}.java"

    def get_test_info_from_parts(self, parts, test_class):
        test_namespace = '/'.join(parts[3:-1])
        test_group = "test_group"
        unit_test_class_name = f"{test_class}TestCase"
        root_path = f"{self.root_dir}/src/test/java/org/apache/fop"
        return test_namespace, test_group, unit_test_class_name, root_path

    def get_build_dir(self, group_name):
        return self.root_dir

    def get_makefile_subfolders(self):
        folder_path = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/fop/build/fop-2.8"
        return [f.path for f in os.scandir(folder_path) if f.is_dir()]

class SpringApp(DaCapoApp):
    def __init__(self, user_prefix):
        super().__init__(user_prefix)
        self.root_dir = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/spring/build"
        self.src_dir = f"{self.root_dir}/src/main/java/org/springframework/samples/petclinic"

    def get_source_path(self, class_name, namespace_name, group_name):
        return f"{self.src_dir}/{namespace_name}/{class_name}.java"

    def get_test_info_from_parts(self, parts, test_class):
        test_namespace = '/'.join(parts[3:-1])
        test_group = "test_group"
        unit_test_class_name = f"{test_class}Tests"
        root_path = f"{self.root_dir}/src/test/java/org/springframework/samples/petclinic"
        return test_namespace, test_group, unit_test_class_name, root_path

    def get_build_dir(self, group_name):
        return self.root_dir

    def get_makefile_subfolders(self):
        folder_path = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/spring"
        return [f.path for f in os.scandir(folder_path) if f.is_dir() and f.name == 'build']

class BioJavaApp(DaCapoApp):
    def __init__(self, user_prefix):
        super().__init__(user_prefix)
        self.root_dir = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/biojava/build"

    def get_source_path(self, class_name, namespace_name, group_name):
        folder_name = "aa-prop" if group_name == "aaproperties" else group_name
        base = f"{self.root_dir}/biojava-{folder_name}/src/main/java/org/biojava/nbio/{group_name}"
        return f"{base}/{namespace_name}/{class_name}.java" if namespace_name else f"{base}/{class_name}.java"

    def get_test_info_from_parts(self, parts, test_class):
        test_namespace = '/'.join(parts[4:-1])
        test_group = parts[3]
        folder_name = "aa-prop" if test_group == "aaproperties" else test_group
        root_path = f"{self.root_dir}/biojava-{folder_name}/src/test/java/org/biojava/nbio/{test_group}"
        unit_test_class_name = f"{test_class}Test"
        return test_namespace, test_group, unit_test_class_name, root_path

    def get_build_dir(self, group_name):
        folder_name = "aa-prop" if group_name == "aaproperties" else group_name
        return f"{self.root_dir}/biojava-{folder_name}"

    def get_makefile_subfolders(self):
        return [f.path for f in os.scandir(self.root_dir) if f.is_dir() and f.name.startswith('biojava-')]

class PmdApp(DaCapoApp):
    def __init__(self, user_prefix):
        super().__init__(user_prefix)
        self.root_dir = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/pmd/build/pmd-core"
        self.src_dir = f"{self.root_dir}/src/main/java/net/sourceforge/pmd"

    def get_source_path(self, class_name, namespace_name, group_name):
        return f"{self.src_dir}/{namespace_name}/{class_name}.java" if namespace_name else f"{self.src_dir}/{class_name}.java"

    def get_test_info_from_parts(self, parts, test_class):
        test_namespace = '/'.join(parts[3:-1])
        test_group = "test_group"
        unit_test_class_name = f"{test_class}Test"
        root_path = f"{self.root_dir}/src/test/java/net/sourceforge/pmd"
        return test_namespace, test_group, unit_test_class_name, root_path

    def get_build_dir(self, group_name):
        return self.root_dir

    def get_makefile_subfolders(self):
        return [f.path for f in os.scandir(os.path.dirname(self.root_dir)) if f.is_dir() and f.name.startswith('pmd-')]

class GraphchiApp(DaCapoApp):
    def __init__(self, user_prefix):
        super().__init__(user_prefix)
        self.root_dir = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/graphchi/build"
        self.src_dir = f"{self.root_dir}/src/main/java/edu/cmu/graphchi"

    def get_source_path(self, class_name, namespace_name, group_name):
        return f"{self.src_dir}/{namespace_name}/{class_name}.java" if namespace_name else f"{self.src_dir}/{class_name}.java"

    def get_test_info_from_parts(self, parts, test_class):
        test_namespace = '/'.join(parts[3:-1])
        test_group = "test_group"
        unit_test_class_name = f"Test{test_class}"
        root_path = f"{self.root_dir}/test/edu/cmu/graphchi"
        return test_namespace, test_group, unit_test_class_name, root_path

    def get_build_dir(self, group_name):
        return self.root_dir

    def get_makefile_subfolders(self):
        folder_path = f"{self.user_prefix}/benchmark_dacapo/benchmarks/bms/graphchi"
        return [f.path for f in os.scandir(folder_path) if f.is_dir() and f.name == 'build']


def get_app(app_name, user_prefix):
    mapping = {
        'fop': FopApp,
        'spring': SpringApp,
        'biojava': BioJavaApp,
        'pmd': PmdApp,
        'graphchi': GraphchiApp
    }
    if app_name not in mapping:
        raise ValueError(f"Unknown DaCapo app: {app_name}")
    return mapping[app_name](user_prefix)
