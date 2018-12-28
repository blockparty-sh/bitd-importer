import base64
from cashaddress import convert
from bitcoin.core.script import CScriptOp
from blockchain_parser.address import Address

def extract(block, tx):
    inputs = []
    outputs = []

    for input_index, item in enumerate(tx.inputs):
        xput = { "i": input_index }

        if not tx.is_coinbase(): # coinbase input doesnt have to be valid script
            for chunk_index, chunk in enumerate(item.script.operations):
                if isinstance(chunk, bytes):
                    xput["b" + str(chunk_index)] = base64.b64encode(chunk).decode("utf-8")
                    xput["h" + str(chunk_index)] = chunk.hex()
                elif isinstance(chunk, CScriptOp):
                    xput["b" + str(chunk_index)] = { "op": int(chunk) }
                else:
                    xput["b" + str(chunk_index)] = chunk

        xput["str"] = item.script.value
        sender = {
            "h": item.transaction_hash,
            "i": item.transaction_index,
        }

        addr = None

        # TODO add additional address types
        if not tx.is_coinbase():
            if len(item.script.operations) == 2: # p2pk
                a = item.script.operations[1]
                if isinstance(a, str) or isinstance(a, bytes): # could be CScriptOp in rare case
                    if len(a) == 33:
                        addr = Address.from_public_key(a).address

        if addr is not None:
            sender['a'] = convert.to_cash_address(addr)[12:] # remove "bitcoincash:" prefix

        xput["e"] = sender
        inputs.append(xput)

    for output_index, item in enumerate(tx.outputs):
        xput = { "i": output_index }

        for chunk_index, chunk in enumerate(item.script.operations):
            if isinstance(chunk, bytes):
                xput["b" + str(chunk_index)] = base64.b64encode(chunk).decode("utf-8")
                try:
                    xput["s" + str(chunk_index)] = chunk.decode("utf-8")
                except UnicodeDecodeError:
                    pass
                xput["h" + str(chunk_index)] = chunk.hex()
            elif isinstance(chunk, CScriptOp):
                xput["b" + str(chunk_index)] = { "op": int(chunk) }
            else:
                xput["b" + str(chunk_index)] = chunk

        xput["str"] = item.script.value

        receiver = {
            "v": item.value,
            "i": output_index
        }
        # bitdb only supports single address, so we will too
        addresses = [str(m.address) for m in item.addresses]
        if len(addresses) == 1:
            receiver["a"] = convert.to_cash_address(addresses[0])[12:] # remove "bitcoincash:" prefix
        xput["e"] = receiver

        outputs.append(xput)


    d = {
        "tx": { "h": tx.hash },
        "in": inputs,
        "out": outputs,
    }

    if block is not None:
        d['blk'] = {
            "i": block.height,
            "h": block.hash,
            "t": block.header.timestamp.strftime("%s")
        }
    return d
