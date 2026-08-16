import json

emails = json.load(open('benchmarks/golden_emails.json'))

new_emails = [
    {
        'id': 'syn_26', 'thread_id': 'thread_rep_1', 'sender': 'boss@work.com',
        'subject': 'Send the quarterly report',
        'body': "Please send the Q3 report by Friday.\n\nAlso, reminder: send the Q3 report.\nAnd don't forget to send the Q3 report.",
        'expected_tasks': 1, 'expected_tp_desc': 'Send the Q3 report'
    },
    {
        'id': 'syn_27', 'thread_id': 'thread_para_1', 'sender': 'boss@work.com',
        'subject': 'Report needed',
        'body': 'I need that report. Make sure you submit the document soon. Provide the file when you can.',
        'expected_tasks': 1, 'expected_tp_desc': 'Submit the report'
    },
    {
        'id': 'syn_28', 'thread_id': 'thread_para_1', 'sender': 'boss@work.com',
        'subject': 'Re: Report needed',
        'body': "Actually, let's make the deadline Monday.",
        'expected_tasks': 1, 'expected_tp_desc': 'Submit the report'
    },
    {
        'id': 'syn_29', 'thread_id': 'thread_comp_1', 'sender': 'boss@work.com',
        'subject': 'Re: The presentation',
        'body': 'Thanks for sending the presentation! It looks great.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_30', 'thread_id': 'thread_assign_1', 'sender': 'manager@work.com',
        'subject': 'Fix the bug',
        'body': 'Hey Team, John will fix the login bug tomorrow.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_31', 'thread_id': 'thread_group_1', 'sender': 'manager@work.com',
        'subject': 'All hands',
        'body': 'Everyone must complete their compliance training by EOD.',
        'expected_tasks': 1, 'expected_tp_desc': 'Complete compliance training'
    },
    {
        'id': 'syn_32', 'thread_id': 'thread_opt_1', 'sender': 'hr@work.com',
        'subject': 'Optional survey',
        'body': 'Feel free to fill out the optional wellbeing survey if you have time.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_33', 'thread_id': 'thread_sec_1', 'sender': 'it@work.com',
        'subject': 'ACTION REQUIRED: Update VPN',
        'body': 'You must update your VPN client immediately to maintain access.',
        'expected_tasks': 1, 'expected_tp_desc': 'Update VPN client'
    },
    {
        'id': 'syn_34', 'thread_id': 'thread_sec_2', 'sender': 'security@work.com',
        'subject': 'New login detected',
        'body': 'We detected a new login from Chrome on Windows. No action is required if this was you.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_35', 'thread_id': 'thread_tx_1', 'sender': 'receipts@store.com',
        'subject': 'Your receipt for order 123',
        'body': 'Thanks for your purchase. Total: $50.00.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_36', 'thread_id': 'thread_ship_1', 'sender': 'tracking@fedex.com',
        'subject': 'Package shipped',
        'body': 'Your package is on the way. Track it here.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_37', 'thread_id': 'thread_cal_1', 'sender': 'calendar@google.com',
        'subject': 'Accepted: Sync meeting',
        'body': 'John accepted the invitation for Sync meeting.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_38', 'thread_id': 'thread_trav_1', 'sender': 'delta@airlines.com',
        'subject': 'Your flight is delayed',
        'body': 'Flight 123 is delayed by 30 minutes. New departure time: 5:30 PM.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_39', 'thread_id': 'thread_mkt_1', 'sender': 'sales@saas.com',
        'subject': 'URGENT: 50% off ends tonight!',
        'body': "Act now! Upgrade your plan before midnight to save 50%. Don't miss out.",
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_40', 'thread_id': 'thread_phish_1', 'sender': 'admin@paypal-secure.com',
        'subject': 'Account Restricted - Verify Immediately',
        'body': 'Your account has been restricted. Click here to verify your identity within 24 hours or lose access.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_41', 'thread_id': 'thread_quote_1', 'sender': 'colleague@work.com',
        'subject': 'Re: Please review',
        'body': 'I finished it.\n> On Monday, you wrote:\n> Please review the attached document.',
        'expected_tasks': 0, 'expected_tp_desc': None
    },
    {
        'id': 'syn_42', 'thread_id': 'thread_fwd_1', 'sender': 'colleague@work.com',
        'subject': 'Fwd: Action required',
        'body': 'FYI.\n---------- Forwarded message ---------\nFrom: IT Dept\nPlease sign the new policy.',
        'expected_tasks': 0, 'expected_tp_desc': None
    }
]

emails.extend(new_emails)
with open('benchmarks/golden_emails.json', 'w') as f:
    json.dump(emails, f, indent=2)
