import numpy as np
import rapidjson as json
from openfermion import InteractionOperator, QubitOperator, IsingOperator, SymbolicOperator
from zquantum.core.utils import (
    SCHEMA_VERSION, convert_dict_to_array, convert_array_to_dict
)
from typing import TextIO, Callable


def convert_interaction_op_to_dict(op: InteractionOperator) -> dict:
    """Convert an InteractionOperator to a dictionary.
    Args:
        op (openfermion.ops.InteractionOperator): the operator
    Returns:
        dictionary (dict): the dictionary representation
    """

    dictionary = {'schema': SCHEMA_VERSION + '-interaction_op'}
    dictionary['constant'] = convert_array_to_dict(np.array(op.constant))
    dictionary['one_body_tensor'] = convert_array_to_dict(np.array(op.one_body_tensor))
    dictionary['two_body_tensor'] = convert_array_to_dict(np.array(op.two_body_tensor))

    return dictionary


def convert_dict_to_interaction_op(dictionary: dict) -> InteractionOperator:
    """Get an InteractionOperator from a dictionary.
    Args:
        dictionary (dict): the dictionary representation
    Returns:
        op (openfermion.ops.InteractionOperator): the operator
    """ 

    # The tolist method is used to convert the constant from a zero-dimensional array to a float/complex
    constant = convert_dict_to_array(dictionary['constant']).tolist()

    one_body_tensor = convert_dict_to_array(dictionary['one_body_tensor'])
    two_body_tensor = convert_dict_to_array(dictionary['two_body_tensor'])

    return InteractionOperator(constant, one_body_tensor, two_body_tensor)


def load_interaction_operator(file: TextIO) -> InteractionOperator:
    """Load an interaction operator object from a file.
    Args:
        file (str or file-like object): the name of the file, or a file-like object.
    
    Returns:
        op (openfermion.ops.InteractionOperator): the operator.
    """

    if isinstance(file, str):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        data = json.load(file)

    return(convert_dict_to_interaction_op(data))


def save_interaction_operator(interaction_operator: InteractionOperator, filename: str) -> None:
    """Save an interaction operator to file.
    Args:
        interaction_operator (InteractionOperator): the operator to be saved
        filename (str): the name of the file
    """

    with open(filename, 'w') as f:
       f.write(json.dumps(convert_interaction_op_to_dict(interaction_operator), indent=2))


def convert_dict_to_qubitop(dictionary: dict) -> QubitOperator:
    """Get a QubitOperator from a dictionary.
    Args:
        dictionary (dict): the dictionary representation
    Returns:
        op (openfermion.ops.QubitOperator): the operator
    """
    return convert_dict_to_operator(dictionary, QubitOperator)


def convert_qubitop_to_dict(op: QubitOperator) -> dict:
    """Convert a QubitOperator to a dictionary.
    Args:
        op (openfermion.ops.QubitOperator): the operator
    Returns:
        dictionary (dict): the dictionary representation
    """

    dictionary = {'schema': SCHEMA_VERSION + '-qubit_op'}
    dictionary['terms'] = []
    for term in op.terms:
        term_dict = {'pauli_ops': [{'qubit': op[0], 'op': op[1]} for op in term]}

        if isinstance(op.terms[term], complex):
            term_dict['coefficient'] = {'real': op.terms[term].real,
                                        'imag': op.terms[term].imag}
        else:
            term_dict['coefficient'] = {'real': op.terms[term].real}

        dictionary['terms'].append(term_dict)

    return dictionary


def convert_dict_to_operator(dictionary: dict, constructor: Callable) -> SymbolicOperator:
    full_operator = constructor()
    for term_dict in dictionary['terms']:
        operator = []
        for pauli_op in term_dict['pauli_ops']:
            operator.append((pauli_op['qubit'], pauli_op['op'])) 
        coefficient = term_dict['coefficient']['real']
        if term_dict['coefficient'].get('imag'):
            coefficient += 1j*term_dict['coefficient']['imag']
        full_operator += constructor(operator, coefficient)

    return full_operator


def save_qubit_operator(qubit_operator: QubitOperator, filename: str) -> None:
    """Save a qubit operator to file.
    Args:
        qubit_operator (QubitOperator): the operator to be saved
        filename (str): the name of the file
    """

    with open(filename, 'w') as f:
       f.write(json.dumps(convert_qubitop_to_dict(qubit_operator), indent=2))


def load_qubit_operator(file: TextIO) -> QubitOperator:
    """Load an operator object from a file.
    Args:
        file (str or file-like object): the name of the file, or a file-like object.
    Returns:
        op (openfermion.ops.QubitOperator): the operator.
    """

    if isinstance(file, str):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        data = json.load(file)

    return(convert_dict_to_qubitop(data))


def convert_isingop_to_dict(op: IsingOperator) -> dict:
    """Convert an IsingOperator to a dictionary.

    Args:
        op (openfermion.ops.IsingOperator): the operator 

    Returns:
        dictionary (dict): the dictionary representation
    """

    dictionary = convert_qubitop_to_dict(op)
    dictionary['schema'] = SCHEMA_VERSION + '-ising_op'
    return dictionary


def convert_dict_to_isingop(dictionary : dict) -> IsingOperator:
    """Get a IsingOperator from a dictionary.

    Args:
        dictionary (dict): the dictionary representation

    Returns:
        op (openfermion.ops.IsingOperator): the operator
    """
    return convert_dict_to_operator(dictionary, IsingOperator)


def load_ising_operator(file: TextIO) -> IsingOperator:
    """Load an Ising operator object from a file.

    Args:
        file (str or file-like object): the name of the file, or a file-like object.

    Returns:
        op (openfermion.ops.IsingOperator): the operator.
    """

    if isinstance(file, str):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        data = json.load(file)

    return(convert_dict_to_isingop(data))


def save_ising_operator(ising_operator:IsingOperator, filename: str) -> None:
    """Save an Ising operator to file.

    Args:
        op (openfermion.IsingOperator): the operator to be saved
        filename (str): the name of the file
    """

    with open(filename, 'w') as f:
       f.write(json.dumps(convert_isingop_to_dict(ising_operator), indent=2))


def save_parameter_grid_evaluation(parameter_grid_evaluation, filename):
    """Save a list of parameter grid evaluations to file

    Args:
        parameter_grid_evaluation (list): List of dicts with a value estimate object under the "value" field
        file (str or file-like object): the name of the file, or a file-like object
    """
    full_dict = {}
    full_dict['schema'] = SCHEMA_VERSION + '-parameter_grid_evaluation'
    dict_list = []
    for evaluation in parameter_grid_evaluation:
        value = evaluation['value'].to_dict()
        value['schema'] = SCHEMA_VERSION + '-value_estimate'
        evaluation['value'] = value
    full_dict['values_set'] = parameter_grid_evaluation

    with open(filename, 'w') as f:
        f.write(json.dumps(full_dict, indent=2))