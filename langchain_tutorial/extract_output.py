# from langchain_community.llms import ollama
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator
from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from typing import Optional, List

import re


ollama_url = "http://localhost:11434"

model = OllamaLLM(model="llama3", base_url=ollama_url, temperature=0, top_k=0, top_p=0)


query = """
PORTARIA Nº 21.091 DE 22 DE JULHO DE 2020. O INSTITUTO DO MEIO AMBIENTE E RECURSOS HÍDRICOS - INEMA, com fulcro nas atribuições e competências 
que lhe foram delegadas pela Lei Estadual n° 12.212/11 e Lei Estadual n° 10.431/06, alterada pela Lei nº 12.377/11, regulamentada pelo Decreto 
Estadual n° 14.024/12 e, tendo em vista o que consta do Processo nº 2020.001.001255/INEMA/LIC-01255, RESOLVE: Art. 1.º - Conceder AUTORIZAÇÃO 
DE SUPRESSÃO DA VEGETAÇÃO NATIVA, válida pelo prazo de 02 (dois) anos a WILSEMAR JOSÉ DORNELES ELGER, inscrito no CPF sob o nº 942.718.605-49 
com sede na Rua Burle Marx, 1553, Jardim Paraíso, no município de Luís Eduardo Magalhães, para implantação de agricultura de sequeiro, em uma 
área de 222,3960 ha na Fazenda São Luís, localizada na Rodovia BA 459, km 65, 31 km, zona rural do município de Formosa do Rio Preto, delimitada 
conforme a poligonal formada pelos pontos sob coordenada geográfica (11° 24’ 07” S / 45° 22’ 59” W) e coordenadas UTM X/Y, mediante o cumprimento 
da legislação vigente e dos condicionantes constantes da íntegra da Portaria que se encontra no referido Processo. Art. 2.º - O rendimento de 
material lenhoso foi estimado em 162,3935 m³, 243,5902 st (stéreo) e 81,1967 MDC. Art. 3.º - Esta portaria aprova o plano de levantamento e 
salvamento de Fauna, incluindo seu manejo e transporte, quando necessário. Art. 4.º - A atividade a que se destina esta supressão de vegetação 
está sujeita ao Procedimento Especial de Licenciamento Ambiental conforme dispõe o anexo IV do Regulamento da Lei 10.431/06, aprovado pelo Decreto 
14.024/12. Art. 5.º - Os produtos e subprodutos originados de atividade autorizada, nas coordenadas de referência (11° 24’ 07” S / 45° 22’ 59” W), 
deverão ser aproveitados conforme estabelecido no Art. 115 da Lei 10.431/2006 sujeitando-se o transporte ao Art. 144 da mesma, bem como à Portaria 
MMA n° 253/2006, que dispõe sobre a necessidade de registro de tais produtos no “Sistema - DOF” para o controle informatizado do transporte e de 
seu armazenamento. Art. 6.º - Estabelecer que esta Autorização, bem como cópias dos documentos relativos ao cumprimento dos condicionantes, deve 
ser mantida disponível à fiscalização dos órgãos do Sistema Estadual de Meio Ambiente - SISEMA. Art. 7.º - Esta portaria não dispensa nem 
substitui a obtenção de certidões, alvarás ou licenças exigidas pela legislação pertinente, federal, estadual ou municipal. Art. 8.º - Esta 
Portaria entrará em vigor na data de sua publicação. MÁRCIA CRISTINA TELLES DE ARAÚJO LIMA - Diretora Geral
"""
# query = "The Fable of the Fox and the Crow"

# Modelo para Endereço
class Endereco(BaseModel):
    cidade: str = Field(..., description="Nome da cidade onde esta localizado o imóvel.", example="São Paulo")
    rua: Optional[str] = Field(default=None, description="Nome da rua do endereço do imóvel. Somente o nome.", example="Rua das Flores")
    numero: Optional[int] = Field(default=None, description="Número do endereço do imóvel. Somente o número.", example=123)
    complemento: Optional[str] = Field(default=None, description="Informações complementares do endereço. Somente se existir no texto.", example="Apto 45")
    bairro: Optional[str] = Field(default=None, description="Nome do bairro. Somente se existir no texto.", example="Centro")
    rodovia: Optional[str] = Field(default=None, description="Numero da rodovia do imóvel. Somente se existir no texto.", example="Centro")
    cep: Optional[str] = Field(default=None, description="Número do CEP. Se existir no texto.", example="12345-678")

class Asv(BaseModel):
    """Informações sobre Autorização de Supressão Nativa extraidas de texto de portaria publicada no diário oficial do Estado da Bahia.
    """
    nro_portaria: str = Field(..., description="Número da portaria. Somente o número.")
    tipo_autorizacao: str = Field(..., description="Tipo de autorização da portaria.")
    validade: int = Field(description="Valido por quanto anos. Somente o número inteiro.")
    cpf: str = Field(description="CPF da pessoa.")
    nro_processo: str = Field(..., description="Número do processo.")
    area_ha: float = Field(description="Quantidade em hectares (ha) da supressão. Somente o número.")
    material_lenhoso_m3: float = Field(description="Quantidade de material lenhoso (m3) da supressão. Somente o número.")
    material_lenhoso_st: float = Field(description="Quantidade de material lenhoso (st) da supressão. Somente o número.")
    material_lenhoso_mdc: float = Field(description="Quantidade de material lenhoso (mdc) da supressão. Somente o número.")
    diretora_geral: str = Field(description="Nome da diretora geral.")
    nome: str = Field(description="Nome da pessoa para envolvida na portaria.")
    motivacao: Optional[str] = Field(description="Para qual finalidade esta portaria foi publicada.")
    endereco: Endereco = Field(description="Endereço da pessoa")
    nome_fazenda: str = Field(description="Nome da fazenda.")

    @field_validator('cpf')
    def format_cpf(cls, value):
        # Remove any non-numeric characters
        digits = re.sub(r'\D', '', value)
        # Check if we have exactly 11 digits
        if len(digits) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        # Format CPF with mask
        formatted_cpf = f'{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}'
        return formatted_cpf


parser = PydanticOutputParser(pydantic_object=Asv)

prompt = PromptTemplate(
    template="""Você é um especialista em coleta de dados de texto do Diário Oficial do Estado da Bahia.
                Seu papel é extrair do texto fornecido os valores exatos para os atributos.
                Se você não souber o valor do atributo perguntado para ser extraído, retorne null para o valor deste atributo.
                \n{format_instructions}\n{query}\n""",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | model | parser

result = chain.invoke({"query": query})

print(result.json())
