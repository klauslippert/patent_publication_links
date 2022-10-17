import sys
import xml.etree.ElementTree as ET
tree = ET.parse(sys.stdin)  
tree.write(sys.stdout, encoding='unicode')
