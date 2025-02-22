import React from "react";
import { useAuthActions } from "../context/AuthContext";
import {
    Button,
    Card,
    Typography,
    List,
    ListItem,
    ListItemPrefix,
    Alert,
} from "@material-tailwind/react";
import { DocumentTextIcon } from "@heroicons/react/24/solid";

export function Sidebar({ onNewConversation }) {
    const [open, setOpen] = React.useState(0);
    const [openAlert, setOpenAlert] = React.useState(true);
    const { logout } = useAuthActions();

    const handleOpen = (value) => {
        setOpen(open === value ? 0 : value);
    };
    return (
        <Card className="sidebar h-[calc(100vh-7rem)] p-4 shadow-xl shadow-blue-gray-900/5 rounded-none border-r border-solid border-custom10Gray">
            <div className="flex flex-row flex-wrap items-center justify-center p-2 pt-5">
                <Button
                    variant="outlined"
                    onClick={onNewConversation} 
                    className="hover:text-white hover:bg-customBlue mb-4 border border-customBlue text-customBlue"
                >
                    Nueva conversación
                </Button>
            </div>
            <List className="min-w-full text-customGray">
                <Typography
                    color="blue-gray"
                    className="flex items-center text-center text-sm font-semibold text-customGray px-1"
                >
                    Histórico
                </Typography>
                <hr className="my-2 border-blue-gray-50" />
                <ListItem>
                    <ListItemPrefix>
                        <DocumentTextIcon className="h-5 w-5" />
                    </ListItemPrefix>
                    7/2/2025 - 15:35
                </ListItem>
            </List>
            <Alert
                open={openAlert}
                className="mt-auto"
                onClose={() => setOpenAlert(false)}
            >
                <Typography variant="h6" className="mb-1">
                    Aviso
                </Typography>
                <Typography variant="small" className="font-normal opacity-80">
                    Las conversaciones con mas de 30 días de antigüedad se
                    eliminarán automáticamente.
                </Typography>
            </Alert>
        </Card>
    );
}
