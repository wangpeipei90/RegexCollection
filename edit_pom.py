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

def agent_pom(pom_file,proj_name):
    print "pom_file: ", pom_file
    print "proj_name: ", proj_name
    tree = ET.parse(pom_file)
    root = tree.getroot()

    #proj_name = root.find("name",namespaces=namespaces).text
    args_agent=arg_agent+proj_name

    ##hanlde surefire maven test javaagent JVM arguments
    plugins=root.find(elem_prefix+"build").find(elem_prefix+"plugins")

    isfound_javaagent=False
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
                 args_CONF=ET.SubElement(plugin_surefire,"configuration")
                 args_JVM=ET.SubElement(args_CONF,"argLine")
                 args_JVM.text=args_agent
            isfound_javaagent=True
            break
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
		elif isinstance(proj,str): 
			agent_pom(pom_file+proj+"/pom.xml",proj)
		else:
			sys.exit('Invalid Input! The arguments are project IDs!')
