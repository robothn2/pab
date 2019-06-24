#coding: utf-8

class Cpus:
    def __init__(self):
        self.hand_write_cpus = [
                ('arm64-v8a', 'arm64', 'aarch64'),
                ('armv7a', 'arm-v7a', 'armeabi', 'arm'),
                ('i686', 'i386', 'x86'),
                ('x86_64', 'x64'),
                ]
        
        self.cpus = []
        self.cpusMap = {}
        for cpus in self.hand_write_cpus:
            if isinstance(cpus, str):
                self.cpus.append(cpus)
                self.cpusMap[cpus] = cpus
            elif isinstance(cpus, tuple):
                self.cpus.extend(cpus)
                for cpu in cpus:
                    self.cpusMap[cpu] = cpus[0]

    def get(self, memberName):
        return self.cpusMap.get(memberName, None)
    