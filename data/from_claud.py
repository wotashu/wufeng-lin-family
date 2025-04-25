import os
from typing import Dict, List, Optional

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.font_manager import FontProperties
from pydantic import BaseModel


# Define Pydantic models for family tree data
class Person(BaseModel):
    id: str  # Person's name as unique identifier
    titles: Optional[List[str]] = None  # List of titles or positions
    parents: List[str] = []  # List of parent IDs
    children: List[str] = []  # List of children IDs
    generation: Optional[int] = None  # Generation number if known
    branch: Optional[str] = None  # Family branch (e.g., "霧峰", "太平")


class FamilyTree(BaseModel):
    name: str  # Name of the family tree
    people: Dict[str, Person]  # Dictionary of Person objects keyed by ID

    def add_person(
        self,
        id: str,
        titles: Optional[List[str]] = None,
        parents: List[str] = [],
        branch: Optional[str] = None,
    ) -> Person:
        """Add a person to the family tree"""
        if id not in self.people:
            self.people[id] = Person(
                id=id,
                titles=titles if titles else None,
                parents=parents.copy(),
                children=[],
                branch=branch,
            )
        else:
            person = self.people[id]
            if titles:
                person.titles = titles
            if parents:
                for parent in parents:
                    if parent not in person.parents:
                        person.parents.append(parent)
            if branch and not person.branch:
                person.branch = branch

        # Add this person as a child to each parent
        for parent_id in parents:
            if parent_id not in self.people:
                self.people[parent_id] = Person(
                    id=parent_id, children=[id], branch=branch
                )
            else:
                parent = self.people[parent_id]
                if id not in parent.children:
                    parent.children.append(id)

        return self.people[id]

    def add_relationship(self, parent_id: str, child_id: str):
        """Add a parent-child relationship"""
        if parent_id not in self.people:
            self.add_person(parent_id)
        if child_id not in self.people:
            self.add_person(child_id)

        parent = self.people[parent_id]
        child = self.people[child_id]

        if child_id not in parent.children:
            parent.children.append(child_id)

        if parent_id not in child.parents:
            child.parents.append(parent_id)

    def compute_generations(self):
        """Compute generation numbers starting from individuals with no parents"""
        roots = [p_id for p_id, person in self.people.items() if not person.parents]
        visited = set()
        generation = 0
        current_level = roots

        while current_level:
            next_level = []
            for person_id in current_level:
                if person_id in visited:
                    continue

                visited.add(person_id)
                person = self.people[person_id]
                person.generation = generation

                next_level.extend(person.children)
            generation += 1
            current_level = next_level

    def to_networkx(self) -> nx.DiGraph:
        """Convert the family tree to a NetworkX DiGraph"""
        G = nx.DiGraph()

        for person_id, person in self.people.items():
            title_text = "\n".join(person.titles) if person.titles else ""
            G.add_node(person_id, titles=title_text, generation=person.generation or 0)

        for person_id, person in self.people.items():
            for child_id in person.children:
                G.add_edge(person_id, child_id)

        return G


def visualize_family_tree(family_tree: FamilyTree, output_file: Optional[str] = None):
    """
    Create a visualization of the family tree

    Args:
        family_tree: FamilyTree model
        output_file: Path to save the image
    """
    family_tree.compute_generations()
    G = family_tree.to_networkx()

    plt.figure(figsize=(16, 12))

    # Set Chinese font for Linux
    # Use a Linux-friendly CJK font such as "Noto Sans CJK TC" if available;
    # fall back on a list of common fonts.
    linux_fonts = [
        "Noto Sans CJK TC",
        "SimHei",
        "Microsoft YaHei",
        "SimSun",
        "NSimSun",
        "FangSong",
        "KaiTi",
    ]
    font_prop = FontProperties(family="Noto Sans CJK TC", size=12)
    for font in linux_fonts:
        if any(f.name == font for f in fm.fontManager.ttflist):
            font_prop = FontProperties(family=font, size=12)
            break

    # Create hierarchical layout by generations
    generations = {}
    for node, data in G.nodes(data=True):
        gen = data.get("generation", 0)
        if gen not in generations:
            generations[gen] = []
        generations[gen].append(node)

    pos = {}
    for gen, nodes in sorted(generations.items()):
        y = -gen
        width = len(nodes)
        for i, node in enumerate(nodes):
            x = (i - width / 2 + 0.5) * 2
            pos[node] = (x, y)

    nx.draw(
        G, pos, with_labels=False, node_size=2000, node_color="lightblue", arrows=True
    )

    node_labels = {}
    for node in G.nodes():
        titles = nx.get_node_attributes(G, "titles").get(node, "")
        node_labels[node] = f"{node}\n{titles}" if titles else node

    nx.draw_networkx_labels(
        G, pos, labels=node_labels, font_family=font_prop.get_name()
    )
    plt.title(family_tree.name, fontproperties=font_prop, fontsize=16)
    plt.axis("off")

    # Use /tmp directory for Linux to store output image
    if output_file:
        plt.savefig(output_file, bbox_inches="tight", dpi=300)
        print(f"Family tree saved to {output_file}")
    else:
        plt.tight_layout()
        plt.show()

    plt.close()


def parse_titles(title_str: str) -> List[str]:
    if not title_str:
        return []
    return [t.strip() for t in title_str.split("\n") if t.strip()]


def create_wufeng_family_tree():
    tree = FamilyTree(name="霧峰林家世系圖", people={})
    titles_data = {
        "林文察": "清知府",
        "林文欽": "清進士",
        "林朝棟": "澄堂 (進士)",
        "林朝楨": "紀堂 (進士)",
        "林朝華": "體堂 (進士)",
        "林朝炳": "敏堂 (獻堂)",
        "林猶龍": "臺灣文化協會經理\n日治豐原市役所議員\n民間蔗糖會議議員",
        "林猶虎": "日治豐原市役所庄長",
        "林垂": "日治大平庄庄長",
        "林烈堂": "日治臺中廳參事",
        "林基兆": "霧峰鄉鄉長",
        "林輯堂": "民國國大代表",
        "林福壽": "明台產物保險公司董事",
        "林福謙": "日治豐原市庄長",
        "林育英": "大同中學教師",
        "林景綸": "彰化銀行經理",
        "林博正": "明治產物董事長",
        "林政光": "明台高中董事長",
        "林明弘": "明台菸酒業\n董富樓\n吉祥齋\n茶園",
        "林享盛": "明台高中副董事長",
    }

    for person_id, title_str in titles_data.items():
        tree.add_person(person_id, titles=parse_titles(title_str), branch="霧峰")

    relationships = [
        ("林文察", "林朝棟"),
        ("林文察", "林祖密"),
        ("林文典", "林朝棟"),
        ("林文欽", "林朝楨"),
        ("林文欽", "林朝華"),
        ("林文欽", "林朝炳"),
        ("林文貴", "林恭"),
        ("林文貴", "林脩"),
        ("林朝棟", "林垂"),
        ("林朝楨", "林烈堂"),
        ("林朝華", "林猶龍"),
        ("林朝炳", "林猶虎"),
        ("林垂", "林基兆"),
        ("林垂", "林基祥"),
        ("林垂", "林垂明"),
        ("林垂", "林垂珠"),
        ("林烈堂", "林輯堂"),
        ("林烈堂", "林猛堂"),
        ("林烈堂", "林爾堂"),
        ("林猶龍", "林福壽"),
        ("林猶虎", "林福謙"),
        ("林基兆", "林育英"),
        ("林基祥", "林幼英"),
        ("林輯堂", "林景綸"),
        ("林輯堂", "林德洲"),
        ("林猛堂", "林德輝"),
        ("林爾堂", "林德勇"),
        ("林福壽", "林博正"),
        ("林福謙", "林政光"),
        ("林博正", "林明弘"),
        ("林政光", "林享盛"),
    ]

    for parent, child in relationships:
        tree.add_relationship(parent, child)

    return tree


def create_taiping_family_tree():
    tree = FamilyTree(name="太平林家世系圖", people={})
    titles_data = {
        "林志芳": "太平祖",
        "林清標": "日治太平庄協議員",
        "林清華": "日治太平庄協議員",
        "林德和": "日治太平庄協議員",
    }
    for person_id, title_str in titles_data.items():
        tree.add_person(person_id, titles=parse_titles(title_str), branch="太平")
    relationships = [
        ("林志芳", "林瑞騰"),
        ("林瑞騰", "林清標"),
        ("林瑞騰", "林清華"),
        ("林清標", "林德和"),
        ("林清華", "林春華"),
        ("林德和", "林春旺"),
        ("林德和", "林春統"),
    ]
    for parent, child in relationships:
        tree.add_relationship(parent, child)
    return tree


def create_wufeng_lower_family_tree():
    tree = FamilyTree(name="霧峰林下厝世系圖", people={})
    titles_data = {
        "林定邦": "霧峰下厝祖",
        "林文察": "清御史\n兵部侍郎\n太子太保\n福建省按察使",
        "林朝棟": "清總兵",
        "林文明": "清副使",
        "林烈堂": "候補知縣\n日治臺中廳參事",
        "林猶龍": "樺仔\n廣東機器局創辦人\n霧峰三秀才",
        "林資彬": "櫟社創辦人\n霧峰三秀才",
        "林資修": "中學\n霧峰三秀才",
        "林正源": "民國國會議員\n第一屆國會亞第一國委",
        "林正德": "民國臺灣省警務處長",
        "林為恭": "北投林本源\n抗日專題列圖\n館長",
    }
    for person_id, title_str in titles_data.items():
        tree.add_person(person_id, titles=parse_titles(title_str), branch="霧峰下厝")
    relationships = [
        ("林定邦", "林文察"),
        ("林文察", "林朝棟"),
        ("林文察", "林文明"),
        ("林文察", "林文彩"),
        ("林朝棟", "林烈堂"),
        ("林朝棟", "林朝堉"),
        ("林朝棟", "林朝奉"),
        ("林朝棟", "林朝燦"),
        ("林朝棟", "林朝薰"),
        ("林朝棟", "林朝炳"),
        ("林烈堂", "林猶龍"),
        ("林烈堂", "林資彬"),
        ("林烈堂", "林資修"),
        ("林烈堂", "林資源"),
        ("林烈堂", "林資鎰"),
        ("林猶龍", "林正源"),
        ("林猶龍", "林正吉"),
        ("林猶龍", "林正德"),
        ("林猶龍", "林正甫"),
        ("林資彬", "林為恭"),
        ("林為恭", "林素功"),
        ("林為恭", "林素彥"),
        ("林為恭", "林素維"),
        ("林為恭", "林素娟"),
        ("林為恭", "林素羚"),
    ]
    for parent, child in relationships:
        tree.add_relationship(parent, child)
    return tree


def create_early_family_tree():
    tree = FamilyTree(name="林家早期世系圖", people={})
    titles_data = {
        "太平祖林志芳": "見下圖",
        "霧峰祖林平侯": "見下圖",
        "霧峰下厝祖林定邦": "見下圖",
        "霧峰頂厝祖林定國": "見下圖",
    }
    for person_id, title_str in titles_data.items():
        tree.add_person(person_id, titles=parse_titles(title_str), branch="早期")
    relationships = [
        ("林名江", "雲湖祖林石"),
        ("林名江", "林壽"),
        ("林名江", "林德"),
        ("林通", "林水"),
        ("林通", "林魏"),
        ("林通", "林森"),
        ("林通", "林大"),
        ("林通", "林適"),
        ("林森", "林德滋"),
        ("林森", "太平祖林志芳"),
        ("林德滋", "霧峰祖林平侯"),
        ("林平侯", "林振祥"),
        ("林平侯", "霧峰下厝祖林定邦"),
        ("林平侯", "霧峰頂厝祖林定國"),
    ]
    for parent, child in relationships:
        tree.add_relationship(parent, child)
    return tree


def main():
    # Use /tmp directory for Linux output
    output_dir = "/tmp/lin_family_trees_pydantic"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    wufeng_tree = create_wufeng_family_tree()
    taiping_tree = create_taiping_family_tree()
    wufeng_lower_tree = create_wufeng_lower_family_tree()
    early_tree = create_early_family_tree()

    visualize_family_tree(
        wufeng_tree, os.path.join(output_dir, "wufeng_lin_family.png")
    )
    visualize_family_tree(
        taiping_tree, os.path.join(output_dir, "taiping_lin_family.png")
    )
    visualize_family_tree(
        wufeng_lower_tree, os.path.join(output_dir, "wufeng_lower_lin_family.png")
    )
    visualize_family_tree(early_tree, os.path.join(output_dir, "early_lin_family.png"))

    print("All family trees generated successfully!")
    person = wufeng_tree.people["林文察"]
    print("\n==== Example of accessing the model data ====")
    print(f"Person: {person.id}")
    print(f"Titles: {person.titles}")
    print(f"Children: {person.children}")
    print(f"Parents: {person.parents}")
    print(f"Generation: {person.generation}")
    print(f"Branch: {person.branch}")


if __name__ == "__main__":
    main()
