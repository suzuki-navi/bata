
import boto3
import botocore

from bata8.lib import *

from bata8.awscloudwatch import *

####################################################################################################

class LambdaPage(MenuPage):
    def canonical(self):
        return ["lambda"]

    def items(self):
        return [
            ("functions", LambdaFunctionsPage),
        ]

class LambdaFunctionsPage(TablePage):
    def canonical(self):
        return ["lambda", "functions"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("lambda", region_name = region)
        ls = client.list_functions()
        items = []
        for elem in ls["Functions"]:
            items.append([elem["FunctionName"]])
        return items

    def detailPage(self, item):
        return LambdaFunctionPage(item[0])

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return LambdaFunctionPage(arg)

class LambdaFunctionPage(MenuPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name]

    def see_also(self):
        cmd1 = ["...", "code", "Location"]
        return [cmd1]

    def items(self):
        return [
            ("code", LambdaFunctionCodePage),
            ("configuration", LambdaFunctionConfigurationPage),
            ("aliases", LambdaFunctionAliasesPage),
            ("metrics", LambdaFunctionMetricsPage),
        ]

    def detailPage(self, item):
        return item[1](self.function_name)

class LambdaFunctionCodePage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "code"]

    def object(self):
        client = session.client("lambda", region_name = region)
        meta = client.get_function(
            FunctionName = self.function_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Code"]

class LambdaFunctionConfigurationPage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "configuration"]

    def object(self):
        client = session.client("lambda", region_name = region)
        meta = client.get_function(
            FunctionName = self.function_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Configuration"]

class LambdaFunctionAliasesPage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "aliases"]

    #def object(self):
    #    client = session.client("lambda", region_name = region)
    #    meta = client.list_aliases(
    #        FunctionName = self.function_name,
    #    )
    #    del(meta["ResponseMetadata"])
    #    return meta

class LambdaFunctionMetricsPage(MenuPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "metrics"]

    def items(self):
        return [
            ("duration", ),
            ("errors", ),
            ("invocations", ),
            ("throttles", ),
        ]

    def detailPage(self, item):
        return CloudWatchMetricsNamespaceMetricDimensionPage("AWS/Lambda", item[0].title(), "FunctionName:{}".format(self.function_name))

####################################################################################################

