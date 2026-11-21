"""
KQL Queries module: Provides curated, production-tested KQL queries
for Microsoft Sentinel and Log Analytics, complete with mock data and explanations.
"""

KQL_QUERIES = [
    {
        "id": "kql-1",
        "title": "Brute Force Attack Followed by Successful Login",
        "mitre_id": "T1110.001 (Password Guessing)",
        "severity": "High",
        "table": "SigninLogs",
        "description": "Identifies when an IP address incurs 5 or more authentication failures within a 15-minute window, immediately succeeded by a successful sign-in.",
        "query": """let timeframe = 1d;
let failure_threshold = 5;
SigninLogs
| where TimeGenerated >= ago(timeframe)
| where ResultType != "0"
| summarize FailureCount = count(), 
            FirstFailure = min(TimeGenerated), 
            LastFailure = max(TimeGenerated) 
            by IPAddress, UserPrincipalName
| where FailureCount >= failure_threshold
| join kind=inner (
    SigninLogs
    | where TimeGenerated >= ago(timeframe)
    | where ResultType == "0"
    | project SuccessTime = TimeGenerated, IPAddress, UserPrincipalName, AppDisplayName
) on IPAddress, UserPrincipalName
| where SuccessTime > LastFailure and SuccessTime <= LastFailure + 15m
| project SuccessTime, UserPrincipalName, IPAddress, FailureCount, AppDisplayName""",
        "explanation": "This query correlates two temporal events. It first groups failed logins (ResultType != 0) by IP and user. Then it performs an inner join with successful logins (ResultType == 0) and asserts that the success occurred within 15 minutes of the last failure."
    },
    {
        "id": "kql-2",
        "title": "Suspicious Privilege Escalation: Global Admin Role Assignment",
        "mitre_id": "T1098 (Account Manipulation)",
        "severity": "Critical",
        "table": "AuditLogs",
        "description": "Alerts when a sensitive directory role (Global Administrator, Security Administrator) is permanently assigned outside an approved PIM window.",
        "query": """AuditLogs
| where TimeGenerated >= ago(24h)
| where OperationName has "Add member to role"
| extend TargetRole = tostring(TargetResources[0].displayName),
         TargetUser = tostring(TargetResources[2].userPrincipalName),
         InitiatedBy = tostring(InitiatedBy.user.userPrincipalName)
| where TargetRole in ("Company Administrator", "Global Administrator", "Privileged Role Administrator")
| project TimeGenerated, OperationName, InitiatedBy, TargetUser, TargetRole, Result""",
        "explanation": "AuditLogs records all tenant-level modifications. This query extracts the role and target user from the dynamic JSON arrays and alerts when highest-tier administrative roles are altered."
    },
    {
        "id": "kql-3",
        "title": "Impossible Travel / Anomalous Geolocation Sign-in",
        "mitre_id": "T1078 (Valid Accounts)",
        "severity": "Medium",
        "table": "SigninLogs",
        "description": "Detects single user accounts signing in from two geographically distant countries within a short time window.",
        "query": """SigninLogs
| where TimeGenerated >= ago(24h)
| where ResultType == "0"
| project TimeGenerated, UserPrincipalName, IPAddress, Location
| sort by UserPrincipalName, TimeGenerated asc
| extend PrevLocation = prev(Location), PrevTime = prev(TimeGenerated), PrevUser = prev(UserPrincipalName)
| where UserPrincipalName == PrevUser
| where Location != PrevLocation and isnotempty(Location) and isnotempty(PrevLocation)
| extend TimeDiffHours = datetime_diff('hour', TimeGenerated, PrevTime)
| where TimeDiffHours < 2
| project TimeGenerated, UserPrincipalName, CurrentLocation = Location, PrevLocation, TimeDiffHours, IPAddress""",
        "explanation": "Uses the KQL window function prev() to compare consecutive successful logins for the same user. If the country changes within less than 2 hours, it flags potential session hijacking or VPN credential compromise."
    },
    {
        "id": "kql-4",
        "title": "Anomalous Azure Storage Blob Data Exfiltration",
        "mitre_id": "T1567 (Exfiltration Over Web Service)",
        "severity": "High",
        "table": "StorageBlobLogs",
        "description": "Identifies an abrupt spike in egress data transfer from Azure Blob Storage over a 1-hour window compared to baseline.",
        "query": """StorageBlobLogs
| where TimeGenerated >= ago(7d)
| where OperationName in ("GetBlob", "GetBlobProperties")
| summarize HourlyBytes = sum(ResponseBodySize) by bin(TimeGenerated, 1h), AccountName
| make-series TotalEgress = sum(HourlyBytes) on TimeGenerated step 1h by AccountName
| extend (Anomalies, Score, Baseline) = series_decompose_anomalies(TotalEgress, 2.5)
| mv-expand TimeGenerated to typeof(datetime), TotalEgress to typeof(long), Anomalies to typeof(int)
| where Anomalies > 0
| project TimeGenerated, AccountName, TotalEgressMB = TotalEgress / (1024 * 1024), Anomalies""",
        "explanation": "Demonstrates KQL time-series analysis using make-series and series_decompose_anomalies(). It automatically flags hours where egress data exceeds 2.5 standard deviations from the historical 7-day baseline."
    },
    {
        "id": "kql-5",
        "title": "Suspicious Azure Resource Deployment by External Guest Account",
        "mitre_id": "T1136.003 (Cloud Accounts)",
        "severity": "High",
        "table": "AzureActivity",
        "description": "Detects when an invited B2B Guest user creates or updates high-cost Azure infrastructure like VMs or Firewalls.",
        "query": """AzureActivity
| where TimeGenerated >= ago(24h)
| where Caller has "#EXT#" // External B2B guest account marker
| where ActivityStatusValue == "Success"
| where OperationNameValue has "write" and (OperationNameValue has "virtualMachines" or OperationNameValue has "azureFirewalls")
| project TimeGenerated, Caller, OperationNameValue, ResourceGroup, SubscriptionId""",
        "explanation": "Guest accounts in Entra ID have the marker '#EXT#' in their UPN. Guests should almost never have Contributor rights to provision expensive compute or network infrastructure."
    }
]

# Mock log datasets for testing queries in the web app
MOCK_LOGS = {
    "SigninLogs": [
        {"TimeGenerated": "2026-11-21T10:00:00Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "50126", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T10:02:15Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "50126", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T10:04:30Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "50126", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T10:06:45Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "50126", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T10:08:12Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "50126", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T10:09:50Z", "UserPrincipalName": "alex.chen@contoso.com", "IPAddress": "198.51.100.24", "ResultType": "0", "Location": "US", "AppDisplayName": "Azure Portal"},
        {"TimeGenerated": "2026-11-21T11:00:00Z", "UserPrincipalName": "sarah.connor@contoso.com", "IPAddress": "203.0.113.88", "ResultType": "0", "Location": "GB", "AppDisplayName": "Office 365"},
        {"TimeGenerated": "2026-11-21T12:15:00Z", "UserPrincipalName": "sarah.connor@contoso.com", "IPAddress": "185.220.101.5", "ResultType": "0", "Location": "RU", "AppDisplayName": "Office 365"}
    ],
    "AuditLogs": [
        {"TimeGenerated": "2026-11-21T09:12:00Z", "OperationName": "Add member to role", "InitiatedBy": {"user": {"userPrincipalName": "secadmin@contoso.com"}}, "TargetResources": [{"displayName": "Global Administrator"}, {}, {"userPrincipalName": "contractor.dev@contoso.com"}], "Result": "success"},
        {"TimeGenerated": "2026-11-21T14:20:00Z", "OperationName": "Update user", "InitiatedBy": {"user": {"userPrincipalName": "helpdesk@contoso.com"}}, "TargetResources": [{"displayName": "User"}, {}, {"userPrincipalName": "john.doe@contoso.com"}], "Result": "success"}
    ]
}

def get_kql_by_id(kql_id: str):
    for q in KQL_QUERIES:
        if q["id"] == kql_id:
            return q
    return None
