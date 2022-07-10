""" Resolve requests to KEGG data Api """

from typing import Any, Optional

from .utils import parse_tsv, request
from .storage import Storage
from .models import Pathway


class Resolver:
    """
    KEGG pathway resolver class.
    Request interface for KEGG API endpoint.
    """

    def __init__(
        self,
        organism: str,
        cachedir: Optional[str] = None
    ) -> None:
        """
        Need 3 letter code as organism identifier.
        :param organism: str
        :param cachedir: str
        """

        self.organism: str = organism

        # Internal storage instance
        self.storage: Storage = Storage(cachedir=cachedir)


    def get_pathway_list(self):
        """
        Request list of pathways linked to organism. {<pathway-id>: <name>}
        :return: dict
        """

        # path:mmu00010	Glycolysis / Gluconeogenesis - Mus musculus (mouse)
        # path:<org><code>\t<name> - <org>

        # Request list of pathways from API
        pathway_list_filename: str = f"pathway_{self.organism}.dump"

        if self.storage.exist(filename=pathway_list_filename):

            # return pathway list dump
            data = self.storage.load_dump(filename=pathway_list_filename)
            return data


        # Data not found in cache. Request from REST api
        data = parse_tsv(
            request(
                url=f"http://rest.kegg.jp/list/pathway/{self.organism}"
            )
        )

        # TODO: save as tsv not binary dump ?


        pathways = {}
        for line in data:
            if len(line) == 2 and line[0] != "":
                pathways[line[0].split(":")[1].strip(self.organism)] = line[1].split(" - ")[0]

        # save as dump
        self.storage.save_dump(filename=pathway_list_filename, data=pathways)

        # return pathway list
        return pathways


    @staticmethod
    def build_url(org: str, code: str) -> str:
        """
        Build path to KGML File at KEGG API endpint
        :param org: str
        :param code: str
        :return: str
        """
        return f"http://rest.kegg.jp/get/{org}{code}/kgml"


    def get_pathway(self, code: str) -> Pathway:
        """
        Request pathway by code
        :param code: str
        :return: KEGGPathway
        """

        pathway_filename: str = f"{self.organism}_path{code}.kgml"
        data: str = ""

        # Check if file exist is storage
        if self.storage.exist(filename=pathway_filename):
            # load from file
            data = self.storage.load(filename=pathway_filename)

        else:
            # request pathway and store
            data = request(
                Resolver.build_url(org=self.organism, code=code)
            )

            self.storage.save(filename=pathway_filename, data=data)

        # Parse string
        return Pathway.parse(data)


    # TODO: are these functions needed ???
    # def link_pathways(self, geneid: str):
    #     """
    #     Return all pathways linked to gene-id
    #     :param geneid: str
    #     :return: list
    #     """
    #     data = parse_tsv(
    #         request(
    #             f"http://rest.kegg.jp/link/pathway/{self.organism}:{geneid}"
    #         )
    #     )

    #     result = []
    #     for item in data:
    #         if len(item) == 2 and item[0] != "":
    #             result.append(item[1])
    #     return result

    # def download_pathways(self, pathways: list):
    #     """
    #     Download all pathways from list of pathway id's.
    #     :param pathways:
    #     :return: NoneType
    #     """
    #     downloads = 0
    #     for code in pathways:
    #         if not self.storage.pathway_file_exist(org=self.organism, code=code):
    #             url = Resolver.build_url(org=self.organism, code=code)

    #             # logging.debug("Requesting path:%s%s %s...", self.organism, code, url)
    #             self.storage.save(filename=f"{self.organism}_path{code}.kgml",
    #                                  data=request(url))
    #             downloads += 1
    #     # logging.debug("Download %d pathway KGML files from KEGG", downloads)


    def get_components(self) -> Any:
        """
        Get dict of components. Request if not in cache
        :return: dict
        """

        # TODO: save as tsv not binary dump

        filename = "compound.dump"
        if not self.storage.exist(filename=filename):
            url = "http://rest.kegg.jp/list/compound/"

            result = {}
            for items in parse_tsv(request(url=url)):
                if len(items) >= 2 and items[0] != "":
                    result[items[0].split(":")[1]] = items[1].split(";")[0]
            self.storage.save_dump(filename=filename, data=result)
            return result

        return self.storage.load_dump(filename=filename)





    # # TODO: remove from storage  --> http request must be performed in resolver
    # @staticmethod
    # def get_organism_list():
    #     """
    #     Get organism codes from file or KEGG API. {<org>: <org-name>}
    #     :return: dict
    #     """
    #     path = KEGGDataStorage.build_path("organism.dump")
    #     organism_list = {}

    #     if not os.path.isfile(path):
    #         # request organism list
    #         result = parse_tsv(request_url(url="http://rest.kegg.jp/list/organism"))
    #         for item in result:
    #             if len(item) == 4 and item[0] != "":
    #                 organism_list[item[1]] = item[2]

    #         with open(path, "wb") as output_file:
    #             pickle.dump(organism_list, output_file)

    #         logging.debug("Request organism list and dump to %s", path)
    #     else:

    #         with open(path, "rb") as input_file:
    #             organism_list = pickle.load(input_file)

    #         logging.debug("Load organism list from %s", path)
    #     return organism_list


    # @staticmethod
    # def get_organism_name(org_code: str):
    #     """
    #     Get full name of organism by 3 letter code
    #     :param org_code: str
    #     :return: str
    #     """

    #     return KEGGDataStorage.get_organism_list().get(org_code, None)


    # @staticmethod
    # def check_organism(org: str):
    #     """
    #     Check if 3 letter organism code exist
    #     :param org: str
    #     :return: bool
    #     """

    #     organism_list = KEGGDataStorage.get_organism_list()
    #     return org in organism_list.keys()


    # @staticmethod
    # def list_existing_pathways():
    #     """
    #     List all KEGG pathway files saved in storage directory. [<filename>]
    #     :return: list
    #     """

    #     # <org>_path<code>.kgml
    #     found = []
    #     pattern = r"[a-z]{3}_path[0-9]{5}\.kgml"
    #     for item in os.listdir(KEGG_DATA):
    #         if re.match(pattern, item, re.IGNORECASE):
    #             found.append(item)
    #     logging.debug("Found %d pathway files", len(found))
    #     return found


    # @staticmethod
    # def pathway_file_to_id(pathway: str):
    #     """
    #     Convert pathway filename to pathway kegg-id
    #     :param pathway: str
    #     :return: str
    #     """

    #     pattern = r"[a-z]{3}_path([0-9]{5})\.kgml"
    #     return re.findall(pattern, pathway, re.IGNORECASE)[0]


    # @staticmethod
    # def pathway_to_id(pathway: str):
    #     """
    #     Extract id from pathway kegg-id
    #     :param pathway: str
    #     :return: str
    #     """

    #     pattern = r"path:[a-z]{3}([0-9]{5})"
    #     return re.findall(pattern, pathway, re.IGNORECASE)[0]


    # @staticmethod
    # def pathway_file_exist(org: str, code: str):
    #     """
    #     Check if pathway file exist in local storage
    #     :param org: str
    #     :param code: str
    #     :return: bool
    #     """

    #     kgml_filename = os.path.join(KEGG_DATA, f"{org}_path{code}.kgml")
    #     return os.path.isfile(kgml_filename)


    # @staticmethod
    # def pathway_list_exist(org: str):
    #     """
    #     Check if list of pathways exists in local stoarage
    #     :param org: str
    #     :return bool
    #     """

    #     return os.path.isfile(os.path.join(KEGG_DATA, f"pathway_{org}.dump"))


    # @staticmethod
    # def load_pathway(org: str, code: str):
    #     """
    #     Load pathway string from local storage.
    #     :param org: str
    #     :param code: str
    #     :return: str
    #     """

    #     if KEGGDataStorage.pathway_file_exist(org=org, code=code):
    #         return KEGGDataStorage.load(f"{org}_path{code}.kgml")

    #     raise FileNotFoundError(
    #         f"Pathway path:{org}{code} not saved in local storage"
    #     )

