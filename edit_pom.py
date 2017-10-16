import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
ET.register_namespace('','http://maven.apache.org/POM/4.0.0')
elem_prefix="{http://maven.apache.org/POM/4.0.0}"
arg_agent='''-javaagent:/home/peipei/RepoReaper/AssistInstrumentation/target/javassist-instrument-1.jar='''

xml_agent='''<!-- executes maven test with -javaagent option -->
            <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <version>2.14</version>
                    <configuration>
                            <skipTests>false</skipTests>
                            <argLine>-javaagent:target/${project.build.finalName}.jar=testUserLog</argLine>
                    </configuration>
            </plugin>'''

xml_javassist='''<dependency>
                        <groupId>org.javassist</groupId>
                        <artifactId>javassist</artifactId>
                        <version>3.14.0-GA</version>
                        <type>jar</type>
                </dependency>'''


#ET.register_namespace('', "http://www.opengis.net/wmts/1.0")
#ET.register_namespace('ows', "http://www.opengis.net/ows/1.1")
#ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
#ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
#ET.register_namespace('gml', "http://www.opengis.net/gml")

def print_subtree(subtree):
    for y in subtree:
        print "\t", y.tag, ":", y.text

#for x in root:
#    print x.tag, x.attrib
#    print_subtree(x.getchildren())

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    #rough_string = ET.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def updateDeps(dependency,groupId,artifactId,version,scope):
    EgroupId=dependency.find(elem_prefix,"groupId")
    if EgroupId is None:
        EgroupId=ET.SubElement(dependency,"groupId")
    EgroupId.text=groupId
    
    EartifactId=dependency.find(elem_prefix,"artifactId")
    if EartifactId is None:
        EartifactId=ET.SubElement(dependency,"artifactId")
    EartifactId.text=artifactId
    
    Eversion=dependency.find(elem_prefix,"version")
    if Eversion is None:
        Eversion=ET.SubElement(dependency,"version")
    Eversion.text=version
    
    Escope=dependency.find(elem_prefix,"scope")
    if Escope is None:
        Escope=ET.SubElement(dependency,"scope")
    Escope.text=scope
#
def addDependency(dependencies,groupId,artifactId,version,scope):
    dependency=ET.SubElement(dependencies,"dependency")
    EgroupId=ET.SubElement(dependency,"groupId")
    EgroupId.text=groupId
    EartifactId=ET.SubElement(dependency,"artifactId")
    EartifactId.text=artifactId
    Eversion=ET.SubElement(dependency,"version")
    Eversion.text=version
    Escope=ET.SubElement(dependency,"scope")
    Escope.text=scope

def addSurefirePlugin(plugins,args_agent):
    plugin=ET.SubElement(plugins,"plugin")
    groupId=ET.SubElement(plugin,"groupId")
    groupId.text="org.apache.maven.plugins"
    
    artifactId=ET.SubElement(plugin,"artifactId")
    artifactId.text="maven-surefire-plugin"
    
    version=ET.SubElement(plugin,"version")
    version.text="2.14"
    configuration=ET.SubElement(plugin,"configuration")
    skipTests=ET.SubElement(configuration,"skipTests")
    skipTests.text="false"
    argLine=ET.SubElement(configuration,"argLine")
    argLine.text=args_agent
    
    
def addAgentProfile(profiles,args_agent):
    profile=ET.SubElement(profiles,"profile")
    #<id>agent</id>
    #<activation>
    #    <activeByDefault>true</activeByDefault>
    #</activation>
    id=ET.SubElement(profile,"id")
    id.text="agent"
    activation=ET.SubElement(profile,"activation")
    activationByDefault=ET.SubElement(activation,"activeByDefault")
    activationByDefault.text="true"
    
    #<build>
    #    <plugins>
    #        <plugin>
    #            <groupId>org.apache.maven.plugins</groupId>
    #            <artifactId>maven-surefire-plugin</artifactId>
    #            <version>2.14</version>
    #            <configuration>
    #                    <skipTests>false</skipTests>
    #                    <argLine>-javaagent:/home/peipei/RepoReaper/AssistInstrumentation/target/javassist-instrument-1.jar=7bk</argLine>
    #            </configuration>
    #        </plugin>
    #    </plugins>
    #</build>
    
    build=ET.SubElement(profile,"build")
    plugins=ET.SubElement(build,"plugins")
    addSurefirePlugin(plugins,args_agent)
    
    dependencies=ET.SubElement(profile,"dependencies")
    addDependency(dependencies,"org.hamcrest","hamcrest-core","1.3","test")
    #<dependencies>
    #            <dependency>
    #                    <groupId>org.hamcrest</groupId>
    #                    <artifactId>hamcrest-core</artifactId>
    #                    <version>1.3</version>
    #                    <scope>test</scope>
    #            </dependency>
    #            <dependency>
    #                    <groupId>org.hamcrest</groupId>
    #                    <artifactId>hamcrest-library</artifactId>
    #                    <version>1.3</version>
    #                    <scope>test</scope>
    #            </dependency>
    addDependency(dependencies,"org.hamcrest","hamcrest-library","1.3","test")
    #            <dependency>
    #                    <groupId>org.mockito</groupId>
    #                    <artifactId>mockito-all</artifactId>
    #                    <version>1.9.5</version>
    #                    <scope>test</scope>
    #            </dependency>
    addDependency(dependencies,"org.mockito","mockito-all","1.9.5","test")
    #            <dependency>
    #                <groupId>junit</groupId>
    #                <artifactId>junit</artifactId>
    #                <version>4.11</version>
    #                <scope>test</scope>
    #            </dependency>
    addDependency(dependencies,"junit","junit","4.11","test")
    #            <dependency>
    #                <groupId>org.ow2.asm</groupId>
    #                <artifactId>asm</artifactId>
    #                <version>4.1</version>
    #            </dependency>
    addDependency(dependencies,"org.ow2.asm","asm","4.1","test")
    #            <dependency>
    #                    <groupId>org.javassist</groupId>
    #                    <artifactId>javassist</artifactId>
    #                    <version>3.14.0-GA</version>
    #                    <type>jar</type>
    #            </dependency>
    addDependency(dependencies,"org.javassist","javassist","3.14.0-GA","test")
    #    </dependencies>
def updateSurefire(surefire_plugin,args_agent):
    args_CONF=surefire_plugin.find(elem_prefix+"configuration")
    if args_CONF is not None:
        args_JVM=args_CONF.find(elem_prefix+"argLine")
        if args_JVM is not None:
            args_JVM.text=args_agent+" "+args_JVM.text
        else:##argLine is missing
            args_JVM=ET.SubElement(args_CONF,"argLine")
            args_JVM.text=args_agent
    else: ##argCONF is missing
        args_CONF=ET.SubElement(surefire_plugin,"configuration")
        args_JVM=ET.SubElement(args_CONF,"argLine")
        args_JVM.text=args_agent
        
def updateProfile(profile,args_agent):
    ##check if surefire exits
    build=profile.find(elem_prefix+"build")
    if build is not None:
        plugins=build.find(elem_prefix+"plugins")
        if plugins is not None:
            ##check if surefire is lists
            is_surefire_plugin=False
            surefire_plugin=None
            for plugin in plugins.findall(elem_prefix+"plugin"):
                artifactId=plugin.find(elem_prefix+"artifactId")
                if artifactId is not None and artifactId.text=="maven-surefire-plugin":
                    surefire_plugin=True
                    surefire_plugin=plugin
                    break
            
            if is_surefire_plugin:
                updateSurefire(surefire_plugin,args_agent)
        else:
            plugins=ET.SubElement(build,"plugins")
            addSurefirePlugin(plugins,args_agent)
    else:
        build=ET.SubElement(profile,"build")
        plugins=ET.SubElement(build,"plugins")
        addSurefirePlugin(plugins,args_agent)         
    
    ##check dependencies
    dependencies=profile.find(elem_prefix+"dependencies")
    if dependencies is None:
        dependencies=ET.SubElement(profile,"dependencies")
    is_javassist=False
    is_hamcrest_core=False
    is_hamcrest_lib=False
    is_junit=False
    is_asm=False
    is_mockito=False
    for dependency in dependencies.findall(elem_prefix+"dependency"):
        artifactId=dependency.find(elem_prefix+"artifactId")
        groupId=dependency.find(elem_prefix+"groupId")
        
        if groupId and artifactId:
            if "org.hamcrest"==groupId and "hamcrest-core"==artifactId:
                is_hamcrest_core=True
                updateDeps(dependency,"org.hamcrest","hamcrest-core","1.3","test")
            elif "org.hamcrest"==groupId and "hamcrest-library"==artifactId:
                is_hamcrest_lib=True
                updateDeps(dependency,"org.hamcrest","hamcrest-library","1.3","test")
            elif "org.mockito"==groupId and "mockito-all"==artifactId:
                is_mockito=True
                updateDeps(dependency,"org.mockito","mockito-all","1.9.5","test")
            elif "junit"==groupId and "junit"==artifactId:
                is_junit=True
                updateDeps(dependency,"junit","junit","4.11","test")
            elif "org.ow2.asm"==groupId and "asm"==artifactId:
                is_asm=True
                updateDeps(dependency,"org.ow2.asm","asm","4.1","test")
            elif "org.javassist"==groupId and "javassist"==artifactId:
                is_javassist=True
                updateDeps(dependency,"org.javassist","javassist","3.14.0-GA","test")
        elif artifactId:
            if "hamcrest-core"==artifactId:
                is_hamcrest_core=True
                updateDeps(dependency,"org.hamcrest","hamcrest-core","1.3","test")
            elif "hamcrest-library"==artifactId:
                is_hamcrest_lib=True
                updateDeps(dependency,"org.hamcrest","hamcrest-library","1.3","test")
            elif "mockito-all"==artifactId:
                is_mockito=True
                updateDeps(dependency,"org.mockito","mockito-all","1.9.5","test")
            elif "junit"==artifactId:
                is_junit=True
                updateDeps(dependency,"junit","junit","4.11","test")
            elif "asm"==artifactId:
                is_asm=True
                updateDeps(dependency,"org.ow2.asm","asm","4.1","test")
            elif "javassist"==artifactId:
                is_javassist=True
                updateDeps(dependency,"org.javassist","javassist","3.14.0-GA","test")            
    if not is_hamcrest_core:
        addDependency(dependencies,"org.hamcrest","hamcrest-core","1.3","test")
    if not is_hamcrest_lib:
        addDependency(dependencies,"org.hamcrest","hamcrest-library","1.3","test")
    if not is_mockito:
        addDependency(dependencies,"org.mockito","mockito-all","1.9.5","test")
    if not is_junit:
        addDependency(dependencies,"junit","junit","4.11","test")
    if not is_asm:
        addDependency(dependencies,"org.ow2.asm","asm","4.1","test")
    if not is_javassist:
        addDependency(dependencies,"org.javassist","javassist","3.14.0-GA","test")
        
def agent_pom(pom_file,proj_name):
    print "pom_file: ", pom_file
    print "proj_name: ", proj_name
    tree = ET.parse(pom_file)
    root = tree.getroot()

    #proj_name = root.find("name",namespaces=namespaces).text
    args_agent=arg_agent+proj_name


    ##Step 1 Check if pom.xml has profiles or not;if profiles exist, update all profiles
    profiles=root.find(elem_prefix+"profiles")
    if profiles is None:
        profiles=ET.SubElement(root,"profiles")
        addAgentProfile(profiles,args_agent)
    else:
        isActivationDefault=False
#        defaultProfile=None
        for profile in profiles.findall(elem_prefix+"profile"):
            activation=profile.find(elem_prefix+"activation")
            if activation is not None:
                activationByDefault=activation.find(elem_prefix+"activeByDefault")
                if activationByDefault is not None and activationByDefault.text=="true":
                        isActivationDefault=True
             #           defaultProfile=profile
            updateProfile(profile,args_agent)
        if not isActivationDefault:
            addAgentProfile(profiles,args_agent)
        
    #ET.dump(root)
    rough_string = ET.tostring(root,'utf-8')
    #rough_string = ET.tostring(elem)
    #reparsed = minidom.parseString(rough_string.encode('utf-8').decode('utf-8'))
   # print reparsed.toprettyxml(indent="  ")
    #file = open("pom.xml", 'wb')
    file = open(pom_file, 'wb')
    file.write(rough_string)
    file.close()
        
                
                
def agent_pom_old(pom_file,proj_name):
    print "pom_file: ", pom_file
    print "proj_name: ", proj_name
    tree = ET.parse(pom_file)
    root = tree.getroot()

    #proj_name = root.find("name",namespaces=namespaces).text
    args_agent=arg_agent+proj_name      
    ##hanlde surefire maven test javaagent JVM arguments
    build=root.find(elem_prefix+"build")
    isfound_javaagent=False
    if build is not None:
        plugins=build.find(elem_prefix+"plugins")
        if plugins is not None:
            for plugin in plugins.findall(elem_prefix+"plugin"):
                artifactId_name=plugin.find(elem_prefix+"artifactId").text
       	#print "plugin artifactId: ", artifactId_name
                #groupId_name=plugin.find(elem_prefix+"groupId").text
       	#print "plugin groupId: ", groupId_name 
        
                #if artifactId_name=="maven-surefire-plugin" and groupId_name=="org.apache.maven.plugins":
                if artifactId_name=="maven-surefire-plugin":
                    args_CONF=plugin.find(elem_prefix+"configuration")
                    if args_CONF is not None:
                        args_JVM=args_CONF.find(elem_prefix+"argLine")
                        if args_JVM is not None:
                            args_JVM.text=args_agent+" "+args_JVM.text
                        else:##argLine is missing
                            args_JVM=ET.SubElement(args_CONF,"argLine")
                            args_JVM.text=args_agent
                    else: ##argCONF is missing
                        args_CONF=ET.SubElement(plugin,"configuration")
                        args_JVM=ET.SubElement(args_CONF,"argLine")
                        args_JVM.text=args_agent
                    isfound_javaagent=True
                    break
        else:
            plugins=ET.SubElement(build,"plugins")
    else:
           build=ET.SubElement(root,"build")
           plugins=ET.SubElement(build,"plugins")
    if not isfound_javaagent:
        plugin_surefire=ET.fromstring(xml_agent)
        plugins.insert(len(plugins),plugin_surefire)
        args_JVM=plugin_surefire.find("configuration").find("argLine")
        args_JVM.text=args_agent
        # <plugin>
        #             <groupId>org.apache.maven.plugins</groupId>
        #             <artifactId>maven-surefire-plugin</artifactId>
        #             <version>2.14</version>
        #             <configuration>
        #                     <skipTests>false</skipTests>
        #                     <argLine>-javaagent:target/${project.build.finalName}.jar=testUserLog</argLine>
        #             </configuration>
        #     </plugin>'''

    deps=root.find(elem_prefix+"dependencies",namespaces=namespaces)
    isfound_javaassist=False
    if deps is None:
        deps=ET.SubElement(root,"dependencies")
    
    for dep in deps.findall(elem_prefix+"dependency"):
        artifactId_name=dep.find(elem_prefix+"artifactId").text
        groupId_name=dep.find(elem_prefix+"groupId").text

        if artifactId_name=="javassist" and groupId_name=="org.javassist":
            isfound_javaassist=True
            break

    if not isfound_javaassist:
        elem_javassist=ET.fromstring(xml_javassist)
        deps.insert(len(deps),elem_javassist)

    #ET.dump(root)
    rough_string = ET.tostring(root,'utf-8')
    #rough_string = ET.tostring(elem)
    #reparsed = minidom.parseString(rough_string.encode('utf-8').decode('utf-8'))
   # print reparsed.toprettyxml(indent="  ")
    #file = open("pom.xml", 'wb')
    file = open(pom_file, 'wb')
    file.write(rough_string)
    file.close()
#end

if __name__== '__main__':
	if sys.argv is None or len(sys.argv)<2:
		sys.exit('Error! You need to specify at least one maven project id!!')
	
	pom_file="/home/peipei/RepoReaper/"
	for proj in sys.argv[1:]:
		if isinstance(proj,(int,long)):
			agent_pom(pom_file+str(proj)+"/pom.xml",str(proj))
			#agent_pom_old(pom_file+str(proj)+"/pom.xml",str(proj))
		elif isinstance(proj,str): 
			agent_pom(pom_file+proj+"/pom.xml",proj)
			#agent_pom_old(pom_file+proj+"/pom.xml",proj)
		else:
			sys.exit('Invalid Input! The arguments are project IDs!')
