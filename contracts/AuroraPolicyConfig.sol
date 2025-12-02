// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuroraPolicyConfig
 * @notice DAO-controlled policy parameters for Aurora Justice Stack
 * 
 * This contract stores policy parameters that can be changed by AuroraDAO governance.
 * Constitution layer (data ethics, recall rights) is immutable and separate.
 * 
 * Only the Governor contract can modify these parameters.
 */
contract AuroraPolicyConfig {
    address public governor;

    struct JusticeParams {
        uint256 decayPerDay;  // CP decay per day
        uint256 baseEko;      // Base CP weight for EKO violations
        uint256 baseCom;      // Base CP weight for COM violations
        uint256 baseSys;      // Base CP weight for SYS violations
        uint256 baseTrust;    // Base CP weight for TRUST violations
    }

    struct RegimeThresholds {
        uint256 softFlag;     // CP threshold for SOFT_FLAG regime
        uint256 probation;    // CP threshold for PROBATION regime
        uint256 restricted;   // CP threshold for RESTRICTED regime
        uint256 lockdown;     // CP threshold for LOCKDOWN regime
    }

    JusticeParams public justiceParams;
    RegimeThresholds public regimeThresholds;

    // Enforcement matrix: regime x action -> allowed
    // Key: keccak256(abi.encodePacked(regime, action))
    mapping(bytes32 => bool) public enforcementMatrix;

    event JusticeParamsUpdated(JusticeParams params);
    event RegimeThresholdsUpdated(RegimeThresholds thresholds);
    event EnforcementUpdated(string indexed regime, string indexed action, bool allowed);
    event GovernorUpdated(address indexed oldGovernor, address indexed newGovernor);

    modifier onlyGovernor() {
        require(msg.sender == governor, "NOT_GOVERNOR");
        _;
    }

    constructor(address _governor) {
        require(_governor != address(0), "INVALID_GOVERNOR");
        governor = _governor;

        // Default values (v1.0)
        justiceParams = JusticeParams({
            decayPerDay: 1,
            baseEko: 10,
            baseCom: 15,
            baseSys: 20,
            baseTrust: 25
        });

        regimeThresholds = RegimeThresholds({
            softFlag: 20,
            probation: 40,
            restricted: 60,
            lockdown: 80
        });
    }

    /**
     * @notice Update justice parameters (CP weights and decay)
     * @dev Only callable by governor
     */
    function setJusticeParams(JusticeParams calldata params) external onlyGovernor {
        require(params.decayPerDay > 0, "INVALID_DECAY");
        require(params.baseEko > 0 && params.baseCom > 0 && params.baseSys > 0 && params.baseTrust > 0, "INVALID_WEIGHTS");
        
        justiceParams = params;
        emit JusticeParamsUpdated(params);
    }

    /**
     * @notice Update regime thresholds
     * @dev Only callable by governor
     * @dev Thresholds must be in ascending order: softFlag < probation < restricted < lockdown
     */
    function setRegimeThresholds(RegimeThresholds calldata thresholds) external onlyGovernor {
        require(
            thresholds.softFlag < thresholds.probation &&
            thresholds.probation < thresholds.restricted &&
            thresholds.restricted < thresholds.lockdown,
            "INVALID_THRESHOLDS"
        );
        
        regimeThresholds = thresholds;
        emit RegimeThresholdsUpdated(thresholds);
    }

    /**
     * @notice Update enforcement matrix entry
     * @dev Only callable by governor
     */
    function setEnforcement(
        string calldata regime,
        string calldata action,
        bool allowed
    ) external onlyGovernor {
        bytes32 key = keccak256(abi.encodePacked(regime, action));
        enforcementMatrix[key] = allowed;
        emit EnforcementUpdated(regime, action, allowed);
    }

    /**
     * @notice Check if action is allowed for regime
     */
    function isAllowed(string calldata regime, string calldata action) external view returns (bool) {
        bytes32 key = keccak256(abi.encodePacked(regime, action));
        return enforcementMatrix[key];
    }

    /**
     * @notice Update governor address (for migration)
     * @dev Only callable by current governor
     */
    function setGovernor(address _newGovernor) external onlyGovernor {
        require(_newGovernor != address(0), "INVALID_GOVERNOR");
        address oldGovernor = governor;
        governor = _newGovernor;
        emit GovernorUpdated(oldGovernor, _newGovernor);
    }
}

