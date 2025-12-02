// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuroraConstitution
 * @notice Immutable constitution hash for Aurora State Network
 * 
 * This contract stores the hash of the Aurora Data Ethics & Transparency Contract.
 * The constitution is immutable and cannot be changed, even by DAO.
 * 
 * This ensures that fundamental rights (data ownership, recall rights, etc.)
 * remain protected regardless of policy changes.
 */
contract AuroraConstitution {
    bytes32 public immutable constitutionHash;
    string public constant version = "v1.0";
    string public constant documentName = "AuroraOS Veri Etiği ve Şeffaflık Sözleşmesi";

    event ConstitutionHashSet(bytes32 indexed hash, string version);

    constructor(bytes32 _hash) {
        require(_hash != bytes32(0), "INVALID_HASH");
        constitutionHash = _hash;
        emit ConstitutionHashSet(_hash, version);
    }

    /**
     * @notice Verify a constitution document against stored hash
     * @param document The constitution document text
     * @return true if document hash matches stored hash
     */
    function verifyConstitution(string calldata document) external view returns (bool) {
        bytes32 documentHash = keccak256(abi.encodePacked(document));
        return documentHash == constitutionHash;
    }
}

